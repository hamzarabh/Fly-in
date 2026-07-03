from parser import syntax_parser
from zone import create_zones , Zone
from visualizer import loop, Drone, Visualizer


data = syntax_parser("config.txt")
nb_drons = data[0]['nb']
zones = create_zones(data)
for z in zones.values():
	if z.type == "start_hub":
		start = z
	if z.type == "end_hub":
		end = z

# f(n) = g(n) + h(n)
def A_start(zones, start, end):
	def manhaten(start_zone):
		xs, ys = start_zone.cordi
		xe, ye = end.cordi
		return (abs(xe - xs) + abs(ye - ys))
	open_list = [(start,0,0,[start.cordi])]
	path = [start.cordi]
	while open_list is not None:
		a = min(open_list,key= lambda x: x[1])
		# for i in open_list:
		# 	print(open_list)
		# if len(open_list) > 1:
		# 	return
		cur_zone, f, g, path = a
		open_list.remove(a)
		if cur_zone is end:
			return path
		cur_zone.closed = True
		neighbors = cur_zone.connection
		for neighbor in neighbors:
			zone = zones[neighbor[0]]
			if zone.zone == "normal":
				new_g = g + 1
			elif zone.zone == "restricted":
				new_g = g + 2
			elif zone.zone == "priority":
				new_g = g + 0
			elif zone.zone == "blocked":
				continue
			if zone.closed is True:
				continue
			h = manhaten(zone)
			new_path = path.copy()
			new_path.append(zone.cordi)
			open_list.append((zone, h + new_g, new_g, new_path))



def simulation(zones, start, end, drones: list):
	nb_drones = len(drones)
	torns = []
	i = 0
	while i < nb_drones:
		i += 1
		torns[str(i)] = 
		d = A_start(zones, start, end)
		for zone in d:
			torns[0]
# print(start.connection)
['af',rte,yrhhj,hrh]



def Create_drones(nb_drones: int,paths: list):
	drones = []
	for i, path in zip(range(1,nb_drones+1),paths):
		drone = Drone("D"+str(i))
		drone.path = path
		drones.append(drone)
	return drones




data = syntax_parser("config.txt")
nb_drons = data[0]['nb']
zones = create_zones(data)
d1 = Drone('D1')
d2 = Drone('D2')
d1.path = [(0,0),(0,1),(2,1),(1,1)]
d2.path = [(0,0),(0,2),(0,1),(2,1)]
d1.localXY = d1.path[0]
d2.localXY = d1.path[0]



drones = Create_drones(nb_drons, [d,d,d,d,d,d,d,d,d,d,d])
v1 = Visualizer(zones,drones)
loop(v1)