from parser import syntax_parser
from zone import create_zones , Zone
from visualizer import loop, Drone, Visualizer
from drone import Drone



# f(n) = g(n) + h(n)
def A_start(zones, start, end, turns):
    def manhaten(start_zone):
        xs, ys = start_zone.cordi
        xe, ye = end.cordi
        return (abs(xe - xs) + abs(ye - ys))
        
    closed_list = []
    open_list = [(start, 0, 0, 0, [start])]
    
    while open_list:
        best_idx = min(range(len(open_list)), key=lambda i: open_list[i][1])
        cur_zone, f, g, t, path = open_list.pop(best_idx)

        if cur_zone is end:
            return path
            
        if (cur_zone.name, t) in closed_list:
            continue
        closed_list.append((cur_zone.name, t))
        
        neighbors = cur_zone.connection
        for neighbor in neighbors:
            zone = zones[neighbor[0]]
            
            if zone.zone == "normal":
                new_g = g + 1
                next_t = t + 1 
            elif zone.zone == "restricted":
                new_g = g + 2
                next_t = t + 2  
            elif zone.zone == "priority":
                new_g = g + 1
                next_t = t + 1
            elif zone.zone == "blocked":
                continue

            if zone is not start and zone is not end:
                if next_t < len(turns):
                    if turns[next_t].count(zone.name) >= zone.max_drones:
                        continue
            
            if (zone.name, next_t) in closed_list:
                continue

            new_path = path.copy()
            if zone.zone == "restricted":
                new_path.append(cur_zone)
            
            h = manhaten(zone)
            if zone.zone == "priority":
                h = h - 2
                
            new_path.append(zone)
            open_list.append((zone, h + new_g, new_g, next_t, new_path))
        
        if cur_zone is not end:
            wait_t = t + 1
            if cur_zone is start or wait_t >= len(turns) or turns[wait_t].count(cur_zone.name) < cur_zone.max_drones:
                if (cur_zone.name, wait_t) not in closed_list:
                    h = manhaten(cur_zone) 
                    new_g = g + 1
                    new_path = path.copy()
                    new_path.append(cur_zone)
                    open_list.append((cur_zone, h + new_g, new_g, wait_t, new_path))
                    
    return None


# def simulation(zones, start, end, nb_drones: int):
#     turns = [[] for _ in range(500)] 
#     paths = []
#     p1 = []
    
#     for j in range(nb_drones):
#         p = A_start(zones, start, end, turns)
#         if j == 0:
#             p1 = p
#         if not p:
#             paths.append(p1)
#             continue
            
#         paths.append(p)
        
#         for i, zone in enumerate(p):
#             while i >= len(turns):
#                 turns.append([])
#             turns[i].append(zone.name)

#     return paths

# # print(start.connection)



# def Create_drones(nb_drones: int,paths: list):
# 	drones = []
# 	for i, path in zip(range(1,nb_drones+1),paths):
# 		drone = Drone("D"+str(i))
# 		pi = []
# 		for z in path:
# 			pi.append(z.cordi)
# 		drone.path = pi
# 		drones.append(drone)
# 	return drones


# d = A_start(zones, start, end)

# data = syntax_parser("config.txt")
# zones = create_zones(data)

# d1 = Drone('D1')
# d2 = Drone('D2')
# d1.path = [(0,0),(0,1),(2,1),(1,1)]
# d2.path = [(0,0),(0,2),(0,1),(2,1)]
# d1.localXY = d1.path[0]
# d2.localXY = d1.path[0]



# drones = Create_drones(nb_drons, [d,d])

# paths = simulation(zones, start, end, nb_drons)
# drones = Create_drones(nb_drons, paths)


data = syntax_parser("maps/linear_path.txt")
nb_drons = data[0]['nb']
zones = create_zones(data)
for z in zones.values():
	if z.type == "start_hub":
		start = z
	if z.type == "end_hub":
		end = z

drones = []

for i in range(nb_drons):
    drone = Drone(
        f"D{i+1}",
        zones,
        start,
        end
    )
    result = drone.FindPath()
    if i == 0 and result is False:
        print("Error: not path in this grafe")
        exit(1)
        

    drones.append(drone)
v1 = Visualizer(zones,drones)
loop(v1)



# for p in paths:
# 	print("[",end="")
# 	for i in p :
# 		print(i.name, end= " ")
# 	print("]",)
	


# مزال لدي مشكلة  في ماكس لينك كاباسيتي لم يصلح