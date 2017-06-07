#Joystick control thread

#imports
import thread
import pygame
import sys
import time
import math
from pygame.locals import *

class Joystick_Thread(threading.Thread):

    def __init__(self, threadID, name, counter):
	pygame.joystick.init()
	pygame.init()
	clock = pygame.time.Clock()
	joy1 = pygame.joystick.Joystick(0)
	joy1.init()

    def run(self):
	while (1):
	    axis1 = joy1.get_axis(0)
	    axis2 = joy1.get_axis(1)
	    axisSpeed = joy1.get_axis(2)


