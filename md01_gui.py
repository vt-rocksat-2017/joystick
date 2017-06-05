#!/usr/bin/env python
import socket
import os
import string
import sys
import time
from optparse import OptionParser
from binascii import *
from md01 import *
from track_gui import *

import pygame
import sys
import time
import math
from  pygame.locals import *

if __name__ == '__main__':
	
    #--------START Command Line option parser------------------------------------------------
    usage = "usage: %prog -a <Server Address> -p <Server Port> "
    parser = OptionParser(usage = usage)
    s_help = "IP address of MD01 Controller, Default: 192.168.42.21"
    p_help = "TCP port number of MD01 Controller, Default: 2000"
    parser.add_option("-a", dest = "ip"  , action = "store", type = "string", default = "192.168.42.21", help = s_help)
    parser.add_option("-p", dest = "port", action = "store", type = "int"   , default = "2000"         , help = p_help)
    (options, args) = parser.parse_args()
    #--------END Command Line option parser-------------------------------------------------

    vhf_uhf_md01 = md01(options.ip, options.port)

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

    app = QtGui.QApplication(sys.argv)
    win = MainWindow(options.ip, options.port)
    win.setCallback(vhf_uhf_md01)
    win.show()
    sys.exit(app.exec_())
    sys.exit()
