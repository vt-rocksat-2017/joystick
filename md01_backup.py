#!/usr/bin/env python
import socket
import os
import string
import sys
import time
import curses
import threading
from binascii import *
from datetime import datetime as date
from optparse import OptionParser

class md01(object):
    def __init__ (self, ip, port, timeout = 1.0, retries = 2):
        self.ip         = ip        #IP Address of MD01 Controller
        self.port       = port      #Port number of MD01 Controller
        self.timeout    = timeout   #Socket Timeout interval, default = 1.0 seconds
        self.connected  = False
        self.retries    = retries   #Number of times to attempt reconnection, default = 2

        self.cmd_az     = 0         #  Commanded Azimuth, used in Set Position Command
        self.cmd_el     = 0         #Commanded Elevation, used in Set Position command
        self.cur_az     = 0         #  Current Azimuth, in degrees, from feedback
        self.cur_el     = 0         #Current Elevation, in degrees, from feedback
        self.cal_az     = 0         #Calibration Angle, used for setting azimuth in calibration mode
        self.cal_el     = 0         #Calibration Angle, used for setting elevation in calibration mode

        self.az_pwr     = 64        #Azimuth motor power setting (decimal value between 0-64)
        self.el_pwr     = 64        #Elevation motor power setting (decimal value between 0-64)

        self.ph         = 10        #  Azimuth Resolution, in pulses per degree, from feedback, default = 10
        self.pv         = 10        #Elevation Resolution, in pulses per degree, from feedback, default = 10

        self.feedback   = ''            #Feedback data from socket
        self.stop_cmd   = bytearray()   #Stop Command Message
        self.status_cmd = bytearray()   #Status Command Message
        self.set_cmd    = bytearray()   #Set Command Message
        self.clean_cmd  = bytearray()   #Clean Command Message, resets calibration angles in MD01 to 0
        self.motor_cmd  = bytearray()   #Joystick motor control command
        self.cal_cmd    = bytearray()   #Calibration Command, sets feedback position to desired angle
        self.power_cmd  = bytearray()   #Set motor power level
        self.init_commands()

    def socketTimeoutEvent(self):
        print "SOCKET TIMEOUT EVENT"

    def init_commands(self):
        #stop command
        for x in [0x57,0,0,0,0,0,0,0,0,0,0,0x0F,0x20]: self.stop_cmd.append(x)      
        
        #Query Status Command
        for x in [0x57,0,0,0,0,0,0,0,0,0,0,0x1F,0x20]: self.status_cmd.append(x)

        #Set Motor Angles Command
        #PH=PV=0x0a, 0x0a = 10, BIG-RAS/HR is 10 pulses per degree
        for x in [0x57,0,0,0,0,0x0a,0,0,0,0,0x0a,0x2F,0x20]: self.set_cmd.append(x) 

        #Move Motor Command
        #PH=PV=0x0a, 0x0a = 10, BIG-RAS/HR is 10 pulses per degree
        for x in [0x57,0,0,0,0,0,0,0,0,0,0,0x14,0x20]: self.motor_cmd.append(x)

        #Clean Motor Angles Command, Calibration Mode
        #Resets Azimuth and Elevation Angles to 0.0 and 0.0 respectively
        #Does NOT cause motors to move, just resets current 'position' to 0 and 0
        for x in [0x57,0,0,0,0,0,0,0,0,0,0,0xF8,0x20]: self.clean_cmd.append(x)      

        #Calibration Message, Cal Mode
        #Set feedback position to desired az/el position
        #Initialized to 0.0 and 0.0 for az and el.
        #byte 2,3,4,5 = azimuth in pulse count form, range:  30-39(dec), ascii value for digit
        #byte 7,8,9,10 = elevation in pulse count form, range: 30-39(dec), assci value for digit
        for x in [0x57,0,0,0,0,0,0,0,0,0,0,0xF9,0x20]: self.cal_cmd.append(x)

        #Set Motor Power Command
        #Initialize motor power to full power 
        #byte 6  = az power, 0-64 decimal, 0x40 = 64(dec)
        #byte 11 = el power, 0-64 decimal, 0x40 = 64(dec)
        for x in [0x57,0,0,0,0,0x40,0,0,0,0,0x40,0xF7,0x20]: self.power_cmd.append(x) 

    def getTimeStampGMT(self):
        return str(date.utcnow()) + " GMT | "

    def connect(self):
        #connect to md01 controller
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.sock.settimeout(self.timeout)   #set socket timeout
        #QtCore.QObject.connect(self.updateTimer, QtCore.SIGNAL('timeout()'), self.queryButtonEvent)
        #self.sock.timeout.connect(self.socketTimeoutEvent)
        print self.getTimeStampGMT() + 'MD01 | Attempting to connect to MD01 Controller: ' + str(self.ip) + ' ' + str(self.port)
        try:
            self.sock.connect((self.ip, self.port))
            self.connected = True
            self.set_motor_power(1,1) #set motors to full power
            print self.getTimeStampGMT() + 'MD01 | Successfully connected to MD01 Controller: ' + str(self.ip) + ' ' + str(self.port)
            return self.connected
            
            #upon connection, get status to determine current antenna position
            #self.get_status()
        except socket.error as msg:
            if (str(msg)=="timed out"): 
                #Callback for network timeout here, trigger reconnect event maybe.
                print "TIMEOUT TIMEOUT TIMEOUT"
            
            print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
            print "Unable to connect to MD01 at IP: " + str(self.ip) + ", Port: " + str(self.port)  
            print "Terminating Program..."
            sys.exit()

    def disconnect(self):
        #disconnect from md01 controller
        print self.getTimeStampGMT() + "MD01 | Attempting to disconnect from MD01 Controller"
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.connected = False
        print self.getTimeStampGMT() + "MD01 | Successfully disconnected from MD01 Controller"
    
    def get_status(self):
        #get azimuth and elevation feedback from md01
        if self.connected == False:
            self.printNotConnected('Get MD01 Status')
            return -1,0,0 #return -1 bad status, 0 for az, 0 for el
        else:
            try:
                self.sock.send(self.status_cmd) 
                self.feedback = self.recv_data()          
            except socket.error as msg:
                print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()
            self.convert_feedback()  
            return 0, self.cur_az, self.cur_el #return 0 good status, feedback az/el 

    def set_stop(self):
        #stop md01 immediately
        if self.connected == False:
            self.printNotConnected('Set Stop')
            return -1, 0, 0
        else:
            try:
                self.sock.send(self.stop_cmd) 
                self.feedback = self.recv_data()          
            except socket.error as msg:
                print "Exception Thrown: " + str(msg) + " (" + str(self.timeout) + "s)"
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()
            self.convert_feedback()
            return 0, self.cur_az, self.cur_el  #return 0 good status, feedback az/el 

######################################################################

    def sendJoystickValues(self):
        if self.connected == False:
            self.printNotConnected('Set Position')
            return -1
        else:
            try:
                print "##########################"
                print hexlify(self.power_cmd)
                print hexlify(self.motor_cmd)
                print "##########################"
                self.sock.send(self.power_cmd) 
                 	
                time.sleep(.3)
                self.sock.send(self.motor_cmd)
            except socket.error as msg:
                print "Exception Thrown: " + str(msg)
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()

######################################################################

    def set_position(self, az, el):
        #set azimuth and elevation of md01
        self.cmd_az = az
        self.cmd_el = el
        self.format_set_cmd()
        if self.connected == False:
            self.printNotConnected('Set Position')
            return -1
        else:
            try:
                self.sock.send(hexlify(self.set_cmd)) 
            except socket.error as msg:
                print "Exception Thrown: " + str(msg)
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()

    def set_cal_angle(self,az,el):
        #set calibration angle
        pass

    def zero_feedback(self):
        #Reset current az and current el position to 0
        if self.connected == False:
            self.printNotConnected('Zero Feedback')
            return -1
        else:
            try:
                self.sock.send(self.clean_cmd) 
            except socket.error as msg:
                print "Exception Thrown: " + str(msg)
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()

    def set_motor_power(self, az_pwr_percent, el_pwr_percent):
        self.az_pwr = int(az_pwr_percent)
        self.el_pwr = int(el_pwr_percent)
        #print "---------------------------------------------"
        #print az_pwr_percent
        self.power_cmd[5] = self.az_pwr
        self.power_cmd[10] = self.el_pwr
        #print self.az_pwr, self.el_pwr, hexlify(self.power_cmd)
        
        if self.connected == False:
            self.printNotConnected('Set Motor Power')
            return -1
        else:
            try:
                self.sock.send(self.power_cmd) 
            except socket.error as msg:
                print "Exception Thrown: " + str(msg)
                print "Closing socket, Terminating program...."
                self.sock.close()
                sys.exit()

    def recv_data2(self):
        #receive socket data
        feedback = ''
        while True:
            c = self.sock.recv(1)
            if hexlify(c) == '20':
                feedback += c
                break
            else:
                feedback += c
        #print hexlify(feedback)
        return feedback


    def recv_data(self):
        #receive socket data
        feedback = ''
        i = 0
        while i < 12:
            c = self.sock.recv(1)
            print str(i) + " " + hexlify(c)
            feedback += c
            i += 1
        #print hexlify(feedback)
        return feedback

    def convert_feedback(self):
        #print "##################################################"
        #fb = hexlify(self.feedback)
        #print len(fb)
        #fb = str(hexlify(self.feedback))
        #print len(fb)
        #print str(fb)
        #print str(str(fb[10]) + str(fb[11]))
        #print int(str(fb[10])+str(fb[11]),16)
        
        fb = self.feedback
         
        h1 = int(str(fb[2])+str(fb[3]),16)
        h2 = int(str(fb[4])+str(fb[5]),16)
        h3 = int(str(fb[6])+str(fb[7]),16)
        h4 = int(str(fb[8])+str(fb[9]),16)
        
        #self.ph = int(str(fb[10])+str(fb[11]),16)
        #ph = int(str(fb[10])+str(fb[11]),16)

        v1 = int(fb[12]+fb[13],16)
        v2 = int(fb[14]+fb[15],16)
        v3 = int(fb[16]+fb[17],16)
        v4 = int(fb[18]+fb[19],16)

        #v1 = int(str(fb[12])+str(fb[13]),16)
        #v2 = int(str(fb[14])+str(fb[15]),16)
        #v3 = int(str(fb[16])+str(fb[17]),16)
        #v4 = int(str(fb[18])+str(fb[19]),16)

        #self.pv = int(str(fb[20])+str(fb[21]),16)

        #pv = int(str(fb[20])+str(fb[21]),16)


        #print self.feedback
        #h1 = ord(self.feedback[1])
        #h2 = ord(self.feedback[2])
        #h3 = ord(self.feedback[3])
        #h4 = ord(self.feedback[4])
        #print h1, h2, h3, h4
        self.cur_az = (h1*100.0 + h2*10.0 + h3 + h4/10.0) - 360.0
        #self.ph = ord(self.feedback[5])

        #v1 = ord(self.feedback[6])
        #v2 = ord(self.feedback[7])
        #v3 = ord(self.feedback[8])
        #v4 = ord(self.feedback[9])

        self.cur_el = (v1*100.0 + v2*10.0 + v3 + v4/10.0) - 360.0
        #self.pv = ord(self.feedback[10])

    def format_set_cmd(self):
        #make sure cmd_az in range -180 to +540
        if   (self.cmd_az>540): self.cmd_az = 540
        elif (self.cmd_az < -180): self.cmd_az = -180
        #make sure cmd_el in range 0 to 180
        if   (self.cmd_el < 0): self.cmd_el = 0
        elif (self.cmd_el>180): self.cmd_el = 180
        
        az = self.cmd_az + 360
        el = self.cmd_el

        az100 = int(az) / 100
        az10 = (int(az) - az100*100) / 10
        az1 = (int(az) - az100*100 - az10*10) / 1
        azpt1 = (az - az100*100 - az10*10 - az1)

        el100 = int(el) / 100
        el10 = (int(el) - el100*100) / 10
        el1 = (int(el) - el100*100 - el10*10) / 1
        elpt1 = (el - el100*100 - el10*10 - el1)

        self.set_cmd[1] = az100
        self.set_cmd[2] = az10
        self.set_cmd[3] = az1
        self.set_cmd[4] = int(azpt1*10)

        self.set_cmd[5] = 1
        
        self.set_cmd[6] = el100
        self.set_cmd[7] = el10
        self.set_cmd[8] = el1
        self.set_cmd[9] = int(elpt1*10)

        self.set_cmd[10] = 1
        print hexlify(self.set_cmd)

        #self.set_cmd[1] = int(self.cmd_az % 100)
        #self.set_cmd[2] = int(self.cmd_az % 10 - self.set_cmd[1]*100)
        #self.set_cmd[3] = int(self.cmd_az % 1 - self.set_cmd[2]*10 - self.set_cmd[1]*100)
        #self.set_cmd[4] = int(self.cmd_az % .1 - self.set_cmd[3] - self.set_cmd[2]*10 - self.set_cmd[1]*100)

        #self.set_cmd[5] = 1
        
        #self.set_cmd[6] = int(self.cmd_el % 100)
        #print self.set_cmd[6]
        #self.set_cmd[7] = int(self.cmd_el % 10 - self.set_cmd[6]*100)
        #self.set_cmd[8] = int(self.cmd_el % 1 - self.set_cmd[7]*10 - self.set_cmd[6]*100)
        #self.set_cmd[9] = int(self.cmd_el % .1 - self.set_cmd[8] - self.set_cmd[7]*10 - self.set_cmd[6]*100)

        #self.set_cmd[10] = 1
        
        

        #self.set_cmd[] = 
        #convert commanded az, el angles into strings
        #cmd_az_str = str(int((float(self.cmd_az) + 360) * self.ph))
        #cmd_el_str = str(int((float(self.cmd_el) + 360) * self.pv))
        #print target_az, len(target_az)
        #ensure strings are 4 characters long, pad with 0s as necessary
        #if   len(cmd_az_str) == 1: cmd_az_str = '000' + cmd_az_str
        #elif len(cmd_az_str) == 2: cmd_az_str = '00'  + cmd_az_str
        #elif len(cmd_az_str) == 3: cmd_az_str = '0'   + cmd_az_str
        #if   len(cmd_el_str) == 1: cmd_el_str = '000' + cmd_el_str
        #elif len(cmd_el_str) == 2: cmd_el_str = '00'  + cmd_el_str
        #elif len(cmd_el_str) == 3: cmd_el_str = '0'   + cmd_el_str
        #print target_az, len(str(target_az)), target_el, len(str(target_el))
        #update Set Command Message
        #self.set_cmd[1] = cmd_az_str[0]
        #self.set_cmd[2] = cmd_az_str[1]
        #self.set_cmd[3] = cmd_az_str[2]
        #self.set_cmd[4] = cmd_az_str[3]
        #self.set_cmd[5] = self.ph
        #self.set_cmd[6] = cmd_el_str[0]
        #self.set_cmd[7] = cmd_el_str[1]
        #self.set_cmd[8] = cmd_el_str[2]
        #self.set_cmd[9] = cmd_el_str[3]
        #self.set_cmd[10] = self.pv

    def printNotConnected(self, msg):
        print self.getTimeStampGMT() + "MD01 | Cannot " + msg + " until connected to MD01 Controller."


