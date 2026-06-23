import pygame
import pygame_menu
import pygame_widgets
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.button import Button
from zone import Zone
from parser import syntax_parser
from zone import create_zones , Zone
pygame.init()


info = pygame.display.Info()

width = info.current_w
height = info.current_h


screen = pygame.display.set_mode((width, height))
run = True


def close_game():
    global run
    run = False
def gred(width: int, height: int):
	x1 = 0
	y1 = 0
	x2 = 0
	y2 = height
	for _ in range(0, width,50):
		x1 += 50
		x2 += 50
		pygame.draw.line(screen,(220,220,220), (x1, y1), (x2, y2),10)
	x1 = 0
	y1 = 0
	x2 = width
	y2 = 0
	for _ in range(0, height,50):
		y1 += 50
		y2 += 50
		pygame.draw.line(screen,(200,200,200), (x1, y1), (x2, y2))
dropdown = Dropdown(
    screen, 
    0, 2,  # x, y
	200, 50,  # width , height
    name='select map',  # name
	fontSize=40,
	margin=20,
    choices=['map1', 'map2', 'map3', 'map4', "map5"], # choices
    borderRadius=5,
    colour=(0, 150, 100),
    textColour=(255, 255, 255),
    direction='down',
    textHAlign='centre'
)
button_run = Button(
    screen, 210, 2, 200, 50,
    text='Run',
    fontSize=20,
    margin=20,
    inactiveColour=(51, 255, 51),  
    pressedColour=(7,125,243),   
    radius=5,
    # onClick=pygame.quit
	)
button_run_step = Button(
	screen,
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
button_reload = Button(
	screen,
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
button_close = Button(
    screen, 840, 2, 200, 50,
    text='Close',
    fontSize=20,
    margin=20,
    inactiveColour=(200, 0, 0),  
    pressedColour=(7,125,243),   
    radius=5,
    onClick=close_game
	)
data = syntax_parser("config.txt")
nb_drons = data[0]['nb']
zones = create_zones(data)

def draw_zone(zone: Zone, screen):
	x = zone.cordi[0]
	y = zone.cordi[1]
	if x < 0:
		x = x + x
	if y < 0:
		y = y + y
	x += 1
	y += 1

	x *= 200
	y *= 200
	pygame.draw.circle(
		screen, zone.color,
		(x,y),
		50, width=0)
	pygame.draw.circle(
		screen, (222,222,10),
		(x,y),
		55, width=4)
while run:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			run = False
	screen.fill((0,0,0))
	pygame.draw.rect(screen, (92,92,92),rect= (0,0,width,54),border_top_left_radius=5,border_top_right_radius=5)


	pygame_widgets.update(events)
	for z in zones.values():
		draw_zone(z, screen)
	# pygame_widgets.draw(screen)
	pygame.display.update()


pygame.quit()