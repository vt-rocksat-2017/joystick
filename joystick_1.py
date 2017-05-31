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
speed = 0

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
	
	oldspeed = speed
	
	#Speed of change
	if (axisSpeed > .75):
		clock.tick(1)
		speed = 10
	elif (axisSpeed > .5):
		clock.tick(2)
		speed = 16
	elif (axisSpeed > .25):
		clock.tick(5)
		speed = 24
	elif (axisSpeed > 0):
		clock.tick(10)
		speed = 32
	elif (axisSpeed > -.25):
		clock.tick(20)
		speed = 40
	elif(axisSpeed > -.5):
		clock.tick(30)
		speed = 48
	elif(axisSpeed > -.75):
		clock.tick(45)
		speed = 56
	else:
		clock.tick(60)
		speed = 64
		
	if (speed != oldspeed): 
		display = "5700000000" + str(speed) + "00000000" + str(speed) + "F720"
		print display
		
	#Changing directions
	if (axis1 < -0.5) and (axis2 < -0.5) and (mufX > 10) and (mufY > 10):
		mufX -= 1
		mufY -= 1
		print ("Up Left - 570500000000000000001420")
	elif (axis1 < -0.5) and (axis2 > 0.5) and (mufX > 10) and (mufY < 900):
		mufX -= 1
		mufY += 1
		print ("DOWN LEFT - 570A00000000000000001420")
	elif (axis1 > 0.5) and (axis2 < -0.5) and (mufX < 650) and (mufY > 10):
		mufX += 1
		mufY -= 1
		print ("UP RIGHT - 570600000000000000001420")
	elif (axis1 > 0.5) and (axis2 > 0.5) and (mufX < 650) and (mufY < 900):
		mufX += 1
		mufY += 1
		print ("DOWN RIGHT - 570900000000000000001420")
	elif (axis1 < -0.5) and (mufX > 10):
		mufX-= 1
		print ("LEFT - 570100000000000000001420")
	elif (axis1 > 0.5) and (mufX < 900):
		mufX += 1
		print ("RIGHT - 570200000000000000001420")
	elif (axis2 < -0.5) and (mufY > 10):
		mufY -= 1
		print ("UP - 570400000000000000001420")
	elif (axis2 > 0.5) and (mufY < 650):
		mufY += 1
		print ("DOWN - 570800000000000000001420")

pygame.joystick.quit()
