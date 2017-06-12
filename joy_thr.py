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
	self.pygame.joystick.init()
	self.pygame.init()
	self.clock = pygame.time.Clock()
	self.joy1 = pygame.joystick.Joystick(0)
	self.joy1.init()

    def run(self):
	while (1):
	    self.axis1 = joy1.get_axis(0)
	    self.axis2 = joy1.get_axis(1)
	    self.axisSpeed = joy1.get_axis(2)

    def stop(self):
	self._stop_event.set()
	self.stopped = True
	
    def stopped(self):
	return self.stopped
