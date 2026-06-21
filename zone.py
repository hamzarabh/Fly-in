from parser import syntax_parser
import webcolors
# rgb = tuple(webcolors.name_to_rgb("green"))

class Zone():
	def __init__(self):
		self.type = None
		self.name = None
		self.cordi = None
		self.max_drones = 1
		self.color = None
		self.zone = "normal"

data = syntax_parser("config.txt")

def color_to_rgb(color: str)-> tuple:
	try:
		return (tuple(webcolors.name_to_rgb(color)))
	except ValueError:
		return (255, 255, 255)


def create_zones(data: list) -> None:
	zones = []
	for item in data:
		zone = Zone()
		if item["type"] in ("start_hub", "end_hub", "hub"):
			zone.type = item["type"]
			zone.name = item["name"]
			zone.cordi = (item["x"],item["y"])
			zone.color = color_to_rgb(item["meta"].get("color"))
			if item["meta"].get("max_drones"):
				zone.max_drones = item["meta"]["max_drones"]
			if item["meta"].get("zone"):
				zone.zone = item["meta"]["zone"]
			zones.append(zone)
	return zones

zones = create_zones(data)
for zone in zones:
	print(zone.name)
	print(zone.type)
	print(zone.cordi)
	print(zone.max_drones)
	print(zone.color)
	print(zone.zone)
	print("---------------")
	