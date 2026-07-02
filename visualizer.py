import pygame
import pygame.freetype as freetype
import pygame_widgets
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.button import Button
from typing import Any
from zone import Zone
from parser import syntax_parser
from zone import create_zones , Zone


clock = pygame.time.Clock()
class Drone():
	def __init__(self, id:str):
		self.id = id
		self.path = []
		self.localIndex = 0
		self.localXY = ()
	def Move(self) -> None:
		self.localIndex += 1


class Visualizer():
	def __init__(self, zones:list, drones: list):
		pygame.init()
		info = pygame.display.Info()
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
		self.start()
	def start(self):
		for drone in self.drones:
			drone.localXY = self.Calcul_XY(
											drone.path[0][0],
							   				drone.path[0][1])


		self.dropdown = Dropdown(
		    self.screen, 
		    0, 2,  # x, y
			200, 50,  # width , height
		    name='select map',  # name
			fontSize=30,
			margin=20,
		    choices=['map1', 'map2', 'map3', 'map4', "map5"], # choices
		    borderRadius=5,
		    colour=(0, 150, 100),
		    textColour=(0, 0, 0),
		    direction='down',
		    textHAlign='centre'
		)

		self.button_run = Button(
		    self.screen, 210, 2, 200, 50,
		    text='Run',
		    fontSize=20,
		    margin=20,
		    inactiveColour=(51, 255, 51),  
		    pressedColour=(7,125,243),   
		    radius=5,
		    # onClick=pygame.quit
			)

		self.button_run_step = Button(
			self.screen,
			420, 2, # x, y
			200 , 50, # width , height
			text='Run step',
			fontSize=20,
			margin=20,
			inactiveColour = (51,255,51),
			pressedColour=(7,125,243),
			radius=5,
			#onClick=
		)

		self.button_reload = Button(
			self.screen,
			630, 2, # x, y
			200 , 50, # width , height
			text='reload',
			fontSize=20,
			margin=20,
			inactiveColour = (255,102,102),
			pressedColour=(7,125,243),
			radius=5,
			#onClick=
		)

		self.button_close = Button(
		    self.screen, 840, 2, 200, 50,
		    text='Close',
		    fontSize=20,
		    margin=20,
		    inactiveColour=(200, 0, 0),  
		    pressedColour=(7,125,243),   
		    radius=5,
		    onClick=self.close_game
			)
	def close_game(self):
		self.run = False
	def Movedrones(self):
		self.move = True
		for drone in self.drones:
			drone.localIndex += 1
	def Calcul_XY(self, x: int, y: int)->tuple:
		x += 1
		y += 1
		x *= 200
		y *= 200
		x = int((x * self.zoom) + self.offset_x)
		y = int((y * self.zoom )+ self.offset_y)
		return (x,y)



def move_drone(vus: Visualizer):
	for drone in vus.drones:
		local = drone.localIndex
		# if local >= len(drone.path):
		# 	break
		x, y  = drone.path[local]
		x, y = vus.Calcul_XY(x, y)
		cuX, cuY = drone.localXY
		if (vus.move is False):
			drone.localXY = (x, y)
			continue
		if (x, y) == (cuX, cuY):
			vus.move = False
			continue
		if (cuX - x) > 0:
			cuX -= 1
		elif (cuX - x) < 0:
			cuX += 1
		if (cuY - y) > 0:
			cuY -= 1
		elif (cuY - y) < 0:
			cuY += 1
		
		drone.localXY = (cuX, cuY)


	



def draw_drone(vus: Visualizer):
	for drone in vus.drones:
		x, y = drone.localXY
		# x = int((x * vus.zoom) + vus.offset_x)
		# y = int((y * vus.zoom )+ vus.offset_y)
		font = freetype.SysFont("Arial", int(15*vus.zoom), bold=True)
		image = pygame.image.load("Copilot_20260630_104836.png")
		new = pygame.transform.smoothscale(image, (60*vus.zoom,100*vus.zoom))
		new = pygame.transform.rotate(new, -90)
		rect = new.get_rect()
		vus.screen.blit(new,(x - (rect.width // 2),y - (rect.height // 2)),rect)
		font.render_to(vus.screen, (x- 20, y - int((20))),drone.id,(255,255,255))


def gred(vus: Visualizer):
	x1 = 0
	y1 = 54
	x2 = 0
	y2 = vus.height
	for _ in range(0, vus.width,70):
		x1 += 70
		x2 += 70
		pygame.draw.line(vus.screen,(200,200,200), (x1, y1), (x2, y2))
	x1 = 0
	y1 = 54
	x2 = vus.width
	y2 = 54
	for _ in range(0, vus.height,70):
		y1 += 70
		y2 += 70
		pygame.draw.line(vus.screen,(200,200,200), (x1, y1), (x2, y2))


def draw_connection(vus: Visualizer):
	for zone in vus.zones.values():
		x, y = zone.cordi
		x , y = vus.Calcul_XY(x,y)
		for z_conn in zone.connection:
			x2 , y2 = vus.zones[z_conn[0]].cordi
			x2 , y2 = vus.Calcul_XY(x2,y2)
			pygame.draw.line(vus.screen,(150,150,255), (x, y), (x2, y2),5)

def draw_zone(zone: Zone, vus: Visualizer):
	zone_surface = (zone.max_drones * 5 ) + 1
	x, y = zone.cordi
	x , y = vus.Calcul_XY(x,y)
	font = freetype.SysFont("Arial", int(15*vus.zoom), bold=True)
	rec = font.get_rect(zone.name, size=15*vus.zoom)
	pygame.draw.circle(
		vus.screen, zone.color,
		(x ,y),
		vus.zoom * (30 + zone_surface), width=0)
	pygame.draw.circle(
		vus.screen, (222,222,10),
		(x,y),
		vus.zoom * (50 + zone_surface), width=4)
	font.render_to(vus.screen, (x- (rec.width // 2), y + int((zone_surface +55) * vus.zoom)),zone.name,(255,255,255))


def loop(vus: Visualizer):
	dragging = False
	current_xy = ()
	while vus.run:
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				vus.run = False
			if event.type == pygame.MOUSEWHEEL:
				if event.y > 0:
					vus.zoom *= 1.1
				elif event.y <= 0 and vus.zoom >= 0.08:
					vus.zoom /= 1.1
				print("zoom:",vus.zoom)
			if event.type == pygame.MOUSEBUTTONDOWN:
					dragging = True
			if event.type == pygame.MOUSEBUTTONUP:
					dragging = False
			if event.type == pygame.MOUSEMOTION and dragging:
				vus.offset_x += event.rel[0]
				vus.offset_y += event.rel[1]
		vus.screen.fill((0,0,0))
		
		gred(vus);
		draw_connection(vus);
		for z in vus.zones.values():
			draw_zone(z, vus)
		pygame.draw.rect(vus.screen, (92,92,92),rect= (0,0,vus.width,54),border_top_left_radius=5,border_top_right_radius=5)
		#pygame.draw.rect(screen, (0,0,0),rect= (0,54,width,height - 54),border_bottom_left_radius=5,border_bottom_right_radius=5)
		pygame_widgets.update(events)
		vus.dropdown.draw()
		vus.button_run.draw()
		vus.button_run_step.draw()
		vus.button_reload.draw()
		vus.button_close.draw()
		if vus.drones[0].localIndex < len(vus.drones[0].path)-2:
			vus.button_run_step.onClick = vus.Movedrones

		
		move_drone(vus)
		draw_drone(vus)
		# vus.drones[0].localIndex = 0
		# for i in vus.drones[0].path[2:]:
		# 	vus.drones[0].Move()
		clock.tick(100)
		# pygame_widgets.draw(screen)
		pygame.display.update()
	pygame.quit()














