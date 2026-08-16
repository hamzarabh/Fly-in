from typing import Any, List
from parser import syntax_parser
from zone import create_zones, Zone
from drone import Drone
import os                                              # noqa
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'         # noqa
import pygame                                          # noqa
import pygame.freetype as freetype                     # noqa
import pygame_widgets                                  # noqa
from pygame_widgets.dropdown import Dropdown           # noqa
from pygame_widgets.button import Button               # noqa

clock = pygame.time.Clock()


class Visualizer:
    """Manage the graphical visualization of the drone simulation."""

    def __init__(self, zones: dict[Any, Any], drones: list) -> None:
        """Initialize the visualizer and its simulation state."""
        pygame.init()
        info = pygame.display.Info()
        self.selected_map: str | None = None
        self.width: int = info.current_w
        self.height: int = info.current_h
        self.zones: dict[Any, Any] = zones
        self.drones: list = drones
        self.screen: Any = pygame.display.set_mode((self.width, self.height))
        self.run: bool = True
        self.zoom: float = 1
        self.offset_x: int = 0
        self.offset_y: int = 0
        self.move: bool = False
        self.turns: int = 0
        self.auto_run: bool = False
        self.logo: Any = pygame.image.load("images/logo.png")
        self.logo = pygame.transform.smoothscale(self.logo, (400, 250))
        self.start()

    def load_map(self) -> None:
        """Load the selected map and initialize its simulation."""
        try:
            data = syntax_parser(f"maps/{self.selected_map}.txt")
            nb_drons = data[0]['nb']

            self.zones = create_zones(data)

            start = None
            end = None
            for z in self.zones.values():
                if z.type == "start_hub":
                    start = z
                if z.type == "end_hub":
                    end = z

            self.drones = []
            for i in range(nb_drons):
                drone: Drone = Drone(f"D{i+1}", self.zones, start, end)
                self.drones.append(drone)

            self.turns = 0
            self.auto_run = False
            self.move = False

            self.start()

        except Exception as e:
            print(f"Error loading map: {e}")

    def start(self) -> None:
        """The method resets zone counters, calculates candidate paths using
        scout drones, distributes the discovered paths among the real
        drones, initializes the starting-zone capacity, and creates the
        map-selection and control widgets.
        """
        # تهيئة counter و planned لكل المناطق
        for z in self.zones.values():
            if z.type == "start_hub":
                z.counter = len(self.drones)
            else:
                z.counter = 0
            z.planned = 0

        paths: List[List[Zone]] = []
        for i in range(2):
            scout_drone = Drone(
                f"scout{i}", self.zones, self.drones[0].start,
                self.drones[0].end)
            if scout_drone.FindPath():
                paths.append(scout_drone.path)
            else:
                break

        if paths:
            path_idx: int = 0
            num_paths: int = len(paths)

            for drone in self.drones:
                drone.path = paths[path_idx]
                drone.localIndex = 0
                drone.localXY = self.Calcul_XY(
                    drone.path[0].cordi[0],
                    drone.path[0].cordi[1]
                )

                path_idx += 1

                if path_idx >= num_paths:
                    path_idx = 0
        else:
            print("Error: not path in this grafe")
            exit(1)

        # if self.drones:
        #     self.drones[0].start.counter = len(self.drones)

        self.dropdown = Dropdown(
            self.screen, 0, 10, 200, 30,
            name='Select map', fontSize=30,
            choices=['linear_path', 'simple_fork', 'basic_capacity',
                     'dead_end_trap', 'circular_loop',
                     'priority_puzzle', 'maze_nightmare', 'capacity_hell',
                     'ultimate_challenge', 'impossible_dream'],
            borderRadius=5, colour=(58, 115, 220),
            textColour=(0, 0, 0), direction='down', textHAlign='centre',
            pressedColour=(255, 153, 51)
        )

        self.button_run = Button(
            self.screen, 210, 10, 200, 30,
            text='Run', fontSize=20,
            inactiveColour=(58, 115, 220),
            pressedColour=(255, 153, 51), radius=5,
        )

        self.button_run_step = Button(
            self.screen, 420, 10, 200, 30,
            text='Run step', fontSize=20,
            inactiveColour=(58, 115, 220),
            pressedColour=(255, 153, 51), radius=5,
        )

        self.button_reload = Button(
            self.screen, 630, 10, 200, 30,
            text='Reload', fontSize=20,
            inactiveColour=(58, 115, 220),
            pressedColour=(255, 153, 51), radius=5,
            onClick=self.reload
        )

        self.button_close = Button(
            self.screen, 840, 10, 200, 30,
            text='Close', fontSize=20, margin=20,
            inactiveColour=(58, 115, 220),
            pressedColour=(255, 153, 51), radius=5,
            onClick=self.close_game
        )

    def reload(self) -> None:
        """Reset the simulation and reinitialize its state.
        The turn counter, automatic execution state, and movement state
        are reset before restarting the simulation.
        """
        self.turns = 0
        self.auto_run = False
        self.move = False
        self.start()

    def close_game(self) -> None:
        """Stop the visualizer main loop."""
        self.run = False

    def Movedrones(self) -> None:
        """Attempt to move all drones by one simulation turn."""
        moved: bool = False
        link_capacity: dict = dict()

        for drone in self.drones:
            if not drone.path:
                continue

            if drone.localIndex < len(drone.path) - 1:
                old_zone = drone.path[drone.localIndex]
                new_zone = drone.path[drone.localIndex + 1]

                if old_zone is new_zone:
                    drone.localIndex += 1
                    moved = True
                    continue

                max_link_capacity = 1
                for zone_name, capacity in old_zone.connection:
                    if zone_name == new_zone.name:
                        max_link_capacity = capacity
                        break

                if new_zone is not drone.end and new_zone is not drone.start:
                    if getattr(new_zone, 'counter', 0) >= new_zone.max_drones:
                        continue

                if (link_capacity.get((old_zone.name, new_zone.name), 0) >=
                        max_link_capacity):
                    continue

                key = (old_zone.name, new_zone.name)
                link_capacity[key] = link_capacity.get(
                    (old_zone.name, new_zone.name), 0) + 1

                old_zone.counter -= 1
                new_zone.counter += 1

                drone.localIndex += 1
                moved = True
                print(f"{drone.id}-{new_zone.name}", end=" ")

        if moved:
            print("")
            self.move = True
            self.turns += 1

    def Calcul_XY(self, x: int, y: int) -> tuple:
        """Convert map coordinates into screen coordinates."""
        x += 1
        y += 1
        x *= 200
        y *= 200
        x = int((x * self.zoom) + self.offset_x)
        y = int((y * self.zoom) + self.offset_y)
        return (x, y)

    def Run(self) -> None:
        """Enable automatic execution of simulation turns."""
        self.auto_run = True


def move_drone(vis: Visualizer) -> None:
    """Move drones smoothly toward their current target positions."""
    finished: bool = True
    speed: int = 10

    for drone in vis.drones:
        if not drone.path:
            continue

        local = drone.localIndex
        if local >= len(drone.path):
            local = len(drone.path) - 1

        target_x, target_y = vis.Calcul_XY(
            drone.path[local].cordi[0],
            drone.path[local].cordi[1]
        )

        if not vis.move:
            drone.localXY = (target_x, target_y)
            continue

        cuX, cuY = drone.localXY

        if abs(cuX - target_x) <= speed:
            cuX = target_x
        elif cuX < target_x:
            cuX += speed
        else:
            cuX -= speed

        if abs(cuY - target_y) <= speed:
            cuY = target_y
        elif cuY < target_y:
            cuY += speed
        else:
            cuY -= speed

        drone.localXY = (cuX, cuY)

        if drone.localXY != (target_x, target_y):
            finished = False

    if finished:
        vis.move = False


def draw_drone(vis: Visualizer) -> None:
    """Draw all active drones on the visualization screen."""
    for drone in vis.drones:
        if not drone.path or not drone.localXY:
            continue

        x, y = drone.localXY
        if y < 60 or y > vis.height + 100 or x < 45 or x > vis.width + 100:
            continue
        font: Any = freetype.SysFont("Arial", int(15 * vis.zoom), bold=True)
        image: Any = pygame.transform.smoothscale(
            drone.image, (int(60 * vis.zoom), int(100 * vis.zoom)))
        image = pygame.transform.rotate(image, -90)
        rect: Any = image.get_rect()
        vis.screen.blit(image, (x - (rect.width // 2), y - (rect.height // 2)))
        text_x: int = int(x - 20 * vis.zoom)
        text_y: int = int(y - 15 * vis.zoom)
        font.render_to(vis.screen, (text_x, text_y), drone.id, (255, 255, 255))


def gred(vis: Visualizer) -> None:
    """Draw the background grid of the visualization."""
    x1, y1, x2, y2 = 0, 54, 0, vis.height

    for _ in range(0, vis.width, 50):
        x1 += 50
        x2 += 50
        pygame.draw.line(vis.screen, (50, 50, 50), (x1, y1), (x2, y2))
    x1, y1, x2, y2 = 0, 54, vis.width, 54
    for _ in range(0, vis.height, 50):
        y1 += 50
        y2 += 50
        pygame.draw.line(vis.screen, (50, 50, 50), (x1, y1), (x2, y2))


def draw_connection(vis: Visualizer) -> None:
    """Draw connections between all connected zones."""
    for zone in vis.zones.values():
        x, y = vis.Calcul_XY(zone.cordi[0], zone.cordi[1])
        if y < 40 or y > vis.height + 100 or x < 45 or x > vis.width + 100:
            continue
        for z_conn in zone.connection:
            x2, y2 = vis.Calcul_XY(
                vis.zones[z_conn[0]].cordi[0], vis.zones[z_conn[0]].cordi[1])
            pygame.draw.line(vis.screen, (150, 150, 255), (x, y), (x2, y2), 5)


def draw_zone(zone: Zone, vis: Visualizer) -> None:
    """Draw a zone and its name on the visualization screen."""
    x, y = vis.Calcul_XY(zone.cordi[0], zone.cordi[1])
    if y < 40 or y > vis.height + 100 or x < 45 or x > vis.width + 100:
        return
    font: Any = freetype.SysFont("Arial", int(15 * vis.zoom), bold=True)
    rec: Any = font.get_rect(zone.name, size=15 * vis.zoom)
    pygame.draw.circle(vis.screen, zone.color, (x, y),
                       vis.zoom * 30, width=0)
    pygame.draw.circle(vis.screen, (222, 222, 10), (x, y),
                       vis.zoom * 50, width=4)
    font.render_to(vis.screen, (x - (rec.width // 2), y +
                   int(55 * vis.zoom)),
                   zone.name, (255, 255, 255))


def loop(vis: Visualizer) -> None:
    """Run the main Pygame event and simulation loop."""
    dragging: bool = False
    pygame.display.set_caption("Fly-in")
    while vis.run:
        vis.screen.fill((0, 0, 0))
        events: Any = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                vis.run = False
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    vis.zoom *= 1.1
                elif event.y <= 0 and vis.zoom >= 0.08:
                    vis.zoom /= 1.1

            if event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                dx, dy = event.rel
                vis.offset_x += dx
                vis.offset_y += dy

                for drone in vis.drones:
                    if drone.localXY:
                        drone.localXY = (
                            drone.localXY[0] + dx, drone.localXY[1] + dy)

        gred(vis)
        draw_connection(vis)
        for z in vis.zones.values():
            draw_zone(z, vis)

        pygame.draw.rect(vis.screen, (92, 92, 92), rect=(
            0, 0, vis.width, 54))
        vis.screen.blit(vis.logo, (vis.width - 360, -100))

        font: Any = freetype.SysFont("Arial", 40, bold=True)
        font.render_to(vis.screen, (1050, 10),
                       f"Turn: {vis.turns}", (255, 153, 51))

        pygame_widgets.update(events)
        if (vis.dropdown.getSelected() is not None and
                vis.selected_map != vis.dropdown.getSelected()):
            vis.selected_map = vis.dropdown.getSelected()
            vis.load_map()
        vis.dropdown.draw()
        vis.button_run.draw()
        vis.button_run_step.draw()
        vis.button_reload.draw()
        vis.button_close.draw()

        vis.button_run_step.onClick = vis.Movedrones
        vis.button_run.onClick = vis.Run

        if vis.auto_run and not vis.move:
            vis.Movedrones()

        move_drone(vis)
        draw_drone(vis)

        pygame.display.update()
        pygame.display.flip()
        clock.tick(40)

    pygame.quit()
