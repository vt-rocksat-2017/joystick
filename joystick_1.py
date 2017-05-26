#imports
import pygame
import sys
import time
import math
from  pygame.locals import *

#defines
BLACK = (0,0,0)
WHITE = (255, 255,255)
done = False
YMIN = 0
YMAX = 768
XMIN = 0
XMAX = 1024
mufY = 10
mufX = 10
#init
pygame.joystick.init()
pygame.init()

screen = pygame.display.set_mode((1024,768))
muf = pygame.image.load('muffin.jpeg')
clock = pygame.time.Clock()

joy1 = pygame.joystick.Joystick(0)
joy1.init()

#LOOP
while done==False:
	for event in pygame.event.get():   #if user did a thing
		if event.type == pygame.QUIT:
			done=True

	screen.fill(WHITE)
	screen.blit(muf,(mufX,mufY))
	pygame.display.flip()

	curY = 0
	curX = 0

	axis1 = joy1.get_axis(0)
	axis2 = joy1.get_axis(1)

	print axis1
	print axis2

	if (axis1 < -0.5) and (mufX > 10):
		mufX-= 1
	if (axis1 > 0.5) and (mufX < 900):
		mufX += 1
	if (axis2 < -0.5) and (mufY > 10):
		mufY -= 1
	if (axis2 > 0.5) and (mufY < 650):
		mufY += 1

	clock.tick(30)

pygame.joystick.quit()
