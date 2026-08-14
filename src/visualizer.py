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
            z.counter = 0
            z.planned = 0

        # --- الخطوة 1: البحث عن أفضل 3 مسارات باستخدام طائرات استكشافية ---
        scout_paths: List[List[Zone]] = []
        for i in range(2):
            scout_drone = Drone(
                f"scout{i}", self.zones, self.drones[0].start,
                self.drones[0].end)
            if scout_drone.FindPath():
                scout_paths.append(scout_drone.path)
            else:
                break  # إذا لم يجد مساراً آخر، نتوقف

        # تصفير العقوبات قبل بدء المحاكاة الحقيقية
        for z in self.zones.values():
            z.planned = 0

        # --- الخطوة 2: توزيع الطائرات الحقيقية على المسارات بالتناوب ---
        if scout_paths:
            path_idx: int = 0  # يبدأ بالمسار الأول
            num_paths: int = len(scout_paths)

            for drone in self.drones:
                # إعطاء المسار الحالي للطائرة
                drone.path = scout_paths[path_idx].copy()
                drone.localIndex = 0
                drone.localXY = self.Calcul_XY(
                    drone.path[0].cordi[0],
                    drone.path[0].cordi[1]
                )

                path_idx += 1

                if path_idx >= num_paths:
                    path_idx = 0

        # تهيئة عداد البداية
        if self.drones:
            self.drones[0].start.counter = len(self.drones)
        # --- إعداد واجهة المستخدم ---
        self.dropdown = Dropdown(
            self.screen, 0, 10, 200, 30,
            name='select map', fontSize=30, margin=20,
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
            text='Run', fontSize=20, margin=20,
            inactiveColour=(58, 115, 220),
            pressedColour=(255, 153, 51), radius=5,
        )

        self.button_run_step = Button(
            self.screen, 420, 10, 200, 30,
            text='Run step', fontSize=20, margin=20,
            inactiveColour=(58, 115, 220),
            pressedColour=(255, 153, 51), radius=5,
        )

        self.button_reload = Button(
            self.screen, 630, 10, 200, 30,
            text='Reload', fontSize=20, margin=20,
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

                # البحث عن سعة الاتصال بشكل صحيح
                max_link_capacity = 1
                for zone_name, capacity in old_zone.connection:
                    if zone_name == new_zone.name:
                        max_link_capacity = capacity
                        break

                # التحقق من سعة المنطقة الوجهة
                if new_zone is not drone.end and new_zone is not drone.start:
                    if getattr(new_zone, 'counter', 0) >= new_zone.max_drones:
                        continue  # المنطقة ممتلئة، انتظر

                # التحقق من سعة الاتصال
                if (link_capacity.get((old_zone.name, new_zone.name), 0) >=
                        max_link_capacity):
                    continue
                # الاتصال ممتلئ، انتظر

                # تسجيل استخدام الاتصال في هذا الدور
                key = (old_zone.name, new_zone.name)
                link_capacity[key] = link_capacity.get(
                    (old_zone.name, new_zone.name), 0) + 1

                # تحديث العدادات
                old_zone.counter = getattr(old_zone, 'counter', 0) - 1
                new_zone.counter = getattr(new_zone, 'counter', 0) + 1

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


def move_drone(vus: Visualizer) -> None:
    """Move drones smoothly toward their current target positions."""
    finished: bool = True
    speed: int = 10

    for drone in vus.drones:
        if not drone.path:
            continue

        local = drone.localIndex
        if local >= len(drone.path):
            local = len(drone.path) - 1

        target_x, target_y = vus.Calcul_XY(
            drone.path[local].cordi[0],
            drone.path[local].cordi[1]
        )

        if not vus.move:
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
        vus.move = False


def draw_drone(vus: Visualizer) -> None:
    """Draw all active drones on the visualization screen."""
    for drone in vus.drones:
        if not drone.path or not drone.localXY:
            continue

        x, y = drone.localXY
        if y < 60 or y > vus.height + 100 or x < 45 or x > vus.width + 100:
            continue
        font: Any = freetype.SysFont("Arial", int(15 * vus.zoom), bold=True)
        new: Any = pygame.transform.smoothscale(
            drone.image, (int(60 * vus.zoom), int(100 * vus.zoom)))
        new = pygame.transform.rotate(new, -90)
        rect: Any = new.get_rect()
        vus.screen.blit(new, (x - (rect.width // 2), y - (rect.height // 2)))
        text_x: int = int(x - 20 * vus.zoom)
        text_y: int = int(y - 15 * vus.zoom)
        font.render_to(vus.screen, (text_x, text_y), drone.id, (255, 255, 255))


def gred(vus: Visualizer) -> None:
    """Draw the background grid of the visualization."""
    x1, y1, x2, y2 = 0, 54, 0, vus.height

    for _ in range(0, vus.width, 50):
        x1 += 50
        x2 += 50
        pygame.draw.line(vus.screen, (50, 50, 50), (x1, y1), (x2, y2))
    x1, y1, x2, y2 = 0, 54, vus.width, 54
    for _ in range(0, vus.height, 50):
        y1 += 50
        y2 += 50
        pygame.draw.line(vus.screen, (50, 50, 50), (x1, y1), (x2, y2))


def draw_connection(vus: Visualizer) -> None:
    """Draw connections between all connected zones."""
    for zone in vus.zones.values():
        x, y = vus.Calcul_XY(zone.cordi[0], zone.cordi[1])
        if y < 40 or y > vus.height + 100 or x < 45 or x > vus.width + 100:
            continue
        for z_conn in zone.connection:
            x2, y2 = vus.Calcul_XY(
                vus.zones[z_conn[0]].cordi[0], vus.zones[z_conn[0]].cordi[1])
            pygame.draw.line(vus.screen, (150, 150, 255), (x, y), (x2, y2), 5)


def draw_zone(zone: Zone, vus: Visualizer) -> None:
    """Draw a zone and its name on the visualization screen."""
    zone_surface: int = (zone.max_drones * 5) + 1
    x, y = vus.Calcul_XY(zone.cordi[0], zone.cordi[1])
    if y < 40 or y > vus.height + 100 or x < 45 or x > vus.width + 100:
        return
    font: Any = freetype.SysFont("Arial", int(15 * vus.zoom), bold=True)
    rec: Any = font.get_rect(zone.name, size=15 * vus.zoom)
    pygame.draw.circle(vus.screen, zone.color, (x, y),
                       vus.zoom * (30 + zone_surface), width=0)
    pygame.draw.circle(vus.screen, (222, 222, 10), (x, y),
                       vus.zoom * (50 + zone_surface), width=4)
    font.render_to(vus.screen, (x - (rec.width // 2), y +
                   int((zone_surface + 55) * vus.zoom)),
                   zone.name, (255, 255, 255))


def loop(vus: Visualizer) -> None:
    """Run the main Pygame event and simulation loop."""
    dragging: bool = False
    pygame.display.set_caption("Fly-in")
    while vus.run:
        vus.screen.fill((0, 0, 0))
        events: Any = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                vus.run = False
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    vus.zoom *= 1.1
                elif event.y <= 0 and vus.zoom >= 0.08:
                    vus.zoom /= 1.1

            if event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                dx, dy = event.rel
                vus.offset_x += dx
                vus.offset_y += dy

                for drone in vus.drones:
                    if drone.localXY:
                        drone.localXY = (
                            drone.localXY[0] + dx, drone.localXY[1] + dy)

        gred(vus)
        draw_connection(vus)
        for z in vus.zones.values():
            draw_zone(z, vus)

        pygame.draw.rect(vus.screen, (92, 92, 92), rect=(
            0, 0, vus.width, 54), border_top_left_radius=5,
            border_top_right_radius=5)
        vus.screen.blit(vus.logo, (vus.width - 360, -100))

        # font = freetype.SysFont("Arial", 40, bold=True)
        # font.render_to(vus.screen, (1050, 10), f"turn:
        #  {vus.turns}", (222, 0, 0))
        font: Any = freetype.SysFont("Arial", 40, bold=True)
        font.render_to(vus.screen, (1050, 10),
                       f"Turn: {vus.turns}", (255, 153, 51))

        pygame_widgets.update(events)
        if (vus.dropdown.getSelected() is not None and
                vus.selected_map != vus.dropdown.getSelected()):
            vus.selected_map = vus.dropdown.getSelected()
            vus.load_map()
        vus.dropdown.draw()
        vus.button_run.draw()
        vus.button_run_step.draw()
        vus.button_reload.draw()
        vus.button_close.draw()

        vus.button_run_step.onClick = vus.Movedrones
        vus.button_run.onClick = vus.Run

        if vus.auto_run and not vus.move:
            vus.Movedrones()

        move_drone(vus)
        draw_drone(vus)

        pygame.display.update()
        pygame.display.flip()
        clock.tick(20)

    pygame.quit()
