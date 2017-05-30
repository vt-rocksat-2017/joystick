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
	axisSpeed = joy1.get_axis(2)

	#Changing directions
	if (axis1 < -0.5) and (mufX > 10):
		mufX-= 1
		print ("LEFT")
	if (axis1 > 0.5) and (mufX < 900):
		mufX += 1
		print ("RIGHT")
	if (axis2 < -0.5) and (mufY > 10):
		mufY -= 1
		print ("UP")
	if (axis2 > 0.5) and (mufY < 650):
		mufY += 1
		print ("DOWN")
	
	#Speed of change
	if (axisSpeed > .75):
		clock.tick(1)
	elif (axisSpeed > .5):
		clock.tick(2)
	elif (axisSpeed > .25):
		clock.tick(5)
	elif (axisSpeed > 0):
		clock.tick(10)
	elif (axisSpeed > -.25):
		clock.tick(20)
	elif(axisSpeed > -.5):
		clock.tick(30)
	elif(axisSpeed > -.75):
		clock.tick(45)
	else:
		clock.tick(60)

pygame.joystick.quit()
