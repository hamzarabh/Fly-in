import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import pygame.freetype as freetype
import pygame_widgets
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.button import Button
from typing import Any, List, Optional
from zone import Zone
from parser import syntax_parser
from zone import create_zones, Zone
from drone import Drone


clock = pygame.time.Clock()

class Visualizer:
    def __init__(self, zones: list, drones: list) -> None:
        pygame.init()
        info = pygame.display.Info()
        self.selected_map = None
        self.width = info.current_w
        self.height = info.current_h
        self.zones = zones
        self.drones = drones
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.run = True
        self.zoom = 1
        self.offset_x = 0
        self.offset_y = 0
        self.move = False
        self.turns = 0
        self.auto_run = False
        self.start()

    def load_map(self):
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
                drone = Drone(f"D{i+1}", self.zones, start, end)
                self.drones.append(drone)
                
            self.turns = 0
            self.auto_run = False
            self.move = False
            
            self.start()
            
        except Exception as e:
            print(f"Error loading map: {e}")

    def start(self) -> None:
        # تهيئة counter و planned لكل المناطق
        for z in self.zones.values():
            z.counter = 0
            z.planned = 0

        # --- الخطوة 1: البحث عن أفضل 3 مسارات باستخدام طائرات استكشافية ---
        scout_paths: List[List[Zone]] = []
        for i in range(2):
            scout_drone = Drone(f"scout{i}", self.zones, self.drones[0].start, self.drones[0].end)
            if scout_drone.FindPath():
                scout_paths.append(scout_drone.path)
            else:
                break  # إذا لم يجد مساراً آخر، نتوقف

        # تصفير العقوبات قبل بدء المحاكاة الحقيقية
        for z in self.zones.values():
            z.planned = 0

        # --- الخطوة 2: توزيع الطائرات الحقيقية على المسارات بالتناوب ---
        if scout_paths:
            path_idx = 0  # يبدأ بالمسار الأول
            num_paths = len(scout_paths)
            
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
        logo = pygame.image.load("logo1.png")
        new = pygame.transform.smoothscale(logo, (200, 50))

        x = self.width - new.get_width()
        y = 0

        self.screen.blit(new, (x, y))
        # --- إعداد واجهة المستخدم ---
        self.dropdown = Dropdown(
            self.screen, 0, 2, 200, 50,
            name='select map', fontSize=30, margin=20,
            choices=['linear_path', 'simple_fork', 'basic_capacity', 'dead_end_trap', 'circular_loop','priority_puzzle','maze_nightmare','capacity_hell','ultimate_challenge','the_impossible_dream'],
            borderRadius=5, colour=(0, 150, 100),
            textColour=(0, 0, 0), direction='down', textHAlign='centre'
        )

        self.button_run = Button(
            self.screen, 210, 2, 200, 50,
            text='Run', fontSize=20, margin=20,
            inactiveColour=(51, 255, 51), pressedColour=(7, 125, 243), radius=5,
        )

        self.button_run_step = Button(
            self.screen, 420, 2, 200, 50,
            text='Run step', fontSize=20, margin=20,
            inactiveColour=(51, 255, 51), pressedColour=(7, 125, 243), radius=5,
        )

        self.button_reload = Button(
            self.screen, 630, 2, 200, 50,
            text='reload', fontSize=20, margin=20,
            inactiveColour=(255, 102, 102), pressedColour=(7, 125, 243), radius=5,
             onClick=self.reload
        )

        self.button_close = Button(
            self.screen, 840, 2, 200, 50,
            text='Close', fontSize=20, margin=20,
            inactiveColour=(200, 0, 0), pressedColour=(7, 125, 243), radius=5,
            onClick=self.close_game
        )
    def reload(self):
        self.turns = 0
        self.auto_run = False
        self.move = False
        self.start()
    
    def close_game(self) -> None:
        self.run = False

    def Movedrones(self) -> None:
        moved = False
        link_capacity = dict()
        
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
                if link_capacity.get((old_zone.name, new_zone.name), 0) >= max_link_capacity:
                    continue  # الاتصال ممتلئ، انتظر

                # تسجيل استخدام الاتصال في هذا الدور
                link_capacity[(old_zone.name, new_zone.name)] = link_capacity.get((old_zone.name, new_zone.name), 0) + 1 

                # تحديث العدادات
                old_zone.counter = getattr(old_zone, 'counter', 0) - 1
                new_zone.counter = getattr(new_zone, 'counter', 0) + 1
                
                drone.localIndex += 1
                moved = True
                print(f"{drone.id}-{new_zone.name}",end=" ")
        
        if moved:
            print("")
            self.move = True
            self.turns += 1

    def Calcul_XY(self, x: int, y: int) -> tuple:
        x += 1
        y += 1
        x *= 200
        y *= 200
        x = int((x * self.zoom) + self.offset_x)
        y = int((y * self.zoom) + self.offset_y)
        return (x, y)

    def Run(self) -> None:
        self.auto_run = True


def move_drone(vus: Visualizer) -> None:
    finished = True
    speed = 10

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
    for drone in vus.drones:
        if not drone.path or not drone.localXY:
            continue

        x, y = drone.localXY
        if y < 60 or y > vus.height + 100 or x < 45 or x > vus.width + 100:
            continue
        font = freetype.SysFont("Arial", int(15 * vus.zoom), bold=True)
        new = pygame.transform.smoothscale(drone.image, (int(60 * vus.zoom), int(100 * vus.zoom)))
        new = pygame.transform.rotate(new, -90)
        rect = new.get_rect()
        vus.screen.blit(new, (x - (rect.width // 2), y - (rect.height // 2)))
        text_x = int(x - 20 * vus.zoom)
        text_y = int(y - 15 * vus.zoom)
        font.render_to(vus.screen, (text_x, text_y), drone.id, (255, 255, 255))


def gred(vus: Visualizer) -> None:
    x1, y1, x2, y2 = 0, 54, 0, vus.height
    
    for _ in range(0, vus.width, 70):
        x1 += 70
        x2 += 70
        pygame.draw.line(vus.screen, (50, 50, 50), (x1, y1), (x2, y2))
    x1, y1, x2, y2 = 0, 54, vus.width, 54
    for _ in range(0, vus.height, 70):
        y1 += 70
        y2 += 70
        pygame.draw.line(vus.screen, (50, 50, 50), (x1, y1), (x2, y2))


def draw_connection(vus: Visualizer) -> None:
    for zone in vus.zones.values():
        x, y = vus.Calcul_XY(zone.cordi[0], zone.cordi[1])
        if y < 40 or y > vus.height + 100 or x < 45 or x > vus.width + 100:
            continue
        for z_conn in zone.connection:
            x2, y2 = vus.Calcul_XY(vus.zones[z_conn[0]].cordi[0], vus.zones[z_conn[0]].cordi[1])
            pygame.draw.line(vus.screen, (150, 150, 255), (x, y), (x2, y2), 5)


def draw_zone(zone: Zone, vus: Visualizer) -> None:
    zone_surface = (zone.max_drones * 5) + 1
    x, y = vus.Calcul_XY(zone.cordi[0], zone.cordi[1])
    if y < 40 or y > vus.height + 100 or x < 45 or x > vus.width + 100:
        return
    font = freetype.SysFont("Arial", int(15 * vus.zoom), bold=True)
    rec = font.get_rect(zone.name, size=15 * vus.zoom)
    pygame.draw.circle(vus.screen, zone.color, (x, y), vus.zoom * (30 + zone_surface), width=0)
    pygame.draw.circle(vus.screen, (222, 222, 10), (x, y), vus.zoom * (50 + zone_surface), width=4)
    font.render_to(vus.screen, (x - (rec.width // 2), y + int((zone_surface + 55) * vus.zoom)), zone.name, (255, 255, 255))


def loop(vus: Visualizer) -> None:
    dragging = False
    while vus.run:
        vus.screen.fill((0, 0, 0))
        events = pygame.event.get()
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
                        drone.localXY = (drone.localXY[0] + dx, drone.localXY[1] + dy)

        gred(vus)
        draw_connection(vus)
        for z in vus.zones.values():
            draw_zone(z, vus)
            
        pygame.draw.rect(vus.screen, (92, 92, 92), rect=(0, 0, vus.width, 54), border_top_left_radius=5, border_top_right_radius=5)
        font = freetype.SysFont("Arial", 40, bold=True)
        font.render_to(vus.screen, (1050, 10), f"turn: {vus.turns}", (222, 0, 0))
        
        pygame_widgets.update(events)
        if vus.dropdown.getSelected() is not None and  vus.selected_map != vus.dropdown.getSelected():
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