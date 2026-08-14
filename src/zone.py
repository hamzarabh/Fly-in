import webcolors
from typing import Any
# rgb = tuple(webcolors.name_to_rgb("green"))


class Zone():
    """Represent a zone in the drone simulation graph.

    A zone contains its identity, coordinates, visual properties,
    drone capacity, zone type, connections, and current simulation state.
    """
    def __init__(self) -> None:
        """Initialize a new zone with default values."""
        self.type: str | None = None
        self.name: str | None = None
        self.cordi: tuple[int, int] = (0, 0)
        self.max_drones: int = 1
        self.color: tuple[int, int, int] = (0, 0, 0)
        self.zone: str | None = "normal"
        self.closed: bool = False
        self.counter: int = 0
        self.planned: int = 0
        self.connection: list[tuple[str, int]] = []


def color_to_rgb(color: str) -> tuple:
    """Convert a color name into an RGB tuple."""
    try:
        return (tuple(webcolors.name_to_rgb(color)))
    except ValueError:
        return (255, 255, 255)


def create_zones(data: list) -> dict[Any, Any]:
    """Create and configure zones from parsed configuration data."""
    zones = {}
    for item in data:
        zone = Zone()
        if item["type"] in ("start_hub", "end_hub", "hub"):
            zone.type = item["type"]
            zone.name = item["name"]
            zone.cordi = (item["x"], item["y"])
            zone.color = color_to_rgb(item["meta"].get("color"))
            if item["meta"].get("max_drones"):
                zone.max_drones = item["meta"]["max_drones"]
            if item["meta"].get("zone"):
                zone.zone = item["meta"]["zone"]
            zones[zone.name] = zone
        if item["type"] == "conection":
            if zones.get(item["zone1"]):
                max_link = item.get("max_link_capacity", 1)
                zone2 = item["zone2"]
                zones[item["zone1"]].connection.append((zone2,
                                                        max_link))
            if zones.get(item["zone2"]):
                max_link = item.get("max_link_capacity", 1)
                zone1 = item["zone1"]
                zones[item["zone2"]].connection.append((zone1,
                                                        max_link))

    return zones


# data = syntax_parser("config.txt")
# zones = create_zones(data)
# for zone in zones.values():
# 	print(zone.name)
# 	print(zone.type)
# 	print(zone.cordi)
# 	print(zone.max_drones)
# 	print(zone.color)
# 	print(zone.connection)
# 	print("---------------")
