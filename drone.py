from typing import Any, List, Optional
from zone import Zone
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
class Drone:
    def __init__(self, id: str, zones: dict, start: Zone, end: Zone) -> None:
        self.id = id
        self.path: List[Zone] = []
        self.localIndex: int = 0
        self.localXY: tuple = ()
        self.zones = zones
        self.start = start
        self.end = end
        self.image = pygame.image.load("Copilot_20260630_104836.png")

    def FindPath(self) -> bool:
        self.path = self.dijkstra()
        if self.path is None:
            return False

        
        # تمييز المسار المختار كـ "مزدحم" للطائرات اللاحقة
        for zone in self.path:
            if zone is not self.start and zone is not self.end:
                zone.planned = getattr(zone, 'planned', 0) + 1
        return True

    def dijkstra(self) -> Optional[List[Zone]]:
        """Simple Dijkstra algorithm with Soft Penalty."""
        
        # العنصر: (g, zone, path)
        open_list: List[tuple] = [(0, self.start, [self.start])]
        closed: set = set()

        while open_list:
            # البحث عن العنصر صاحب أقل تكلفة (g)
            best_zone = min(open_list, key=lambda x: x[0])
            open_list.remove(best_zone)

            g, cur_zone, path = best_zone

            if cur_zone is self.end:
                return path

            if cur_zone.name in closed:
                continue
            closed.add(cur_zone.name)

            for neighbor in cur_zone.connection:
                zone = self.zones[neighbor[0]]

                if zone.zone == "normal":
                    new_g = g + 1
                elif zone.zone == "restricted":
                    new_g = g + 2
                elif zone.zone == "priority":
                    new_g = g + 1
                elif zone.zone == "blocked":
                    continue

                if zone.name in closed:
                    continue

                # --- العقوبة الناعمة (Soft Penalty) ---
                planned_count = getattr(zone, 'planned', 0)
                if planned_count > 0:
                    new_g += planned_count * 3

                if zone.zone == "priority":
                    new_g -= 1
                new_path = path.copy()
                if zone.zone == "restricted":
                    new_path.append(zone)  # إضافة مرتين للمناطق المقيدة
                new_path.append(zone)

                open_list.append((new_g, zone, new_path))

        return None