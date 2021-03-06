#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt

import PyQt4.Qwt5 as Qwt
import numpy as np
from datetime import datetime as date
import sys
from az_QwtDial import *
from el_QwtDial import *
import time
import pygame
import thread
import threading
from pygame.locals import *


class MainWindow(QtGui.QWidget):
    def __init__(self, ip, port):
        QtGui.QMainWindow.__init__(self)

        self.resize(700, 630)
        self.setFixedWidth(700)
        self.setFixedHeight(700)
        self.setWindowTitle('MD01 Controller v1.0')
        self.setContentsMargins(0,0,0,0)

        self.ip = ip
        self.port = port

        self.cur_az = 0
        self.tar_az = 0
        self.cur_el = 0
        self.tar_el = 0
        self.home_az = 0.0
        self.home_el = 0.0

        self.callback    = None   #Callback accessor for tracking control
        self.connected   = False  #Status of TCP/IP connection to MD-01
        self.update_rate = 250    #Feedback Query Auto Update Interval in milliseconds
        self.update_refresh_rate = 250 #Initial joystick sync rate
        self.update_motor_control_rate = 250 #Initial motor signal rate


        self.initUI()
        self.darken()
        self.setFocus()

    def initUI(self):
        self.initFrames()
        self.initAzimuth()
        self.initElevation()
        self.initControls()
        self.initMotorCtrl()
        self.initNet()

        self.initJoy()

	self.initJoystick()
        self.connectSignals()
#####################################################################

    def initJoy(self):
        pygame.display.init()
        pygame.joystick.init()
	self.joy1 = pygame.joystick.Joystick(0)
	self.joy1.init()
        self.refreshJoy()

    def refreshJoy(self):
        pygame.event.pump()

        self.axisAz = self.joy1.get_axis(0)
	self.axisEl = self.joy1.get_axis(1)
	self.axisSpeed = -1*self.joy1.get_axis(2)

        print self.axisAz, self.axisEl, self.axisSpeed
#####################################################################


    def setCallback(self, callback):
        self.callback = callback

    def connectSignals(self):
        self.azPlusPtOneButton.clicked.connect(self.azPlusPtOneButtonClicked)
        self.azPlusOneButton.clicked.connect(self.azPlusOneButtonClicked)
        self.azPlusTenButton.clicked.connect(self.azPlusTenButtonClicked)
        self.azMinusPtOneButton.clicked.connect(self.azMinusPtOneButtonClicked)
        self.azMinusOneButton.clicked.connect(self.azMinusOneButtonClicked)
        self.azMinusTenButton.clicked.connect(self.azMinusTenButtonClicked)
        self.azTextBox.returnPressed.connect(self.azTextBoxReturnPressed)

        self.elPlusPtOneButton.clicked.connect(self.elPlusPtOneButtonClicked)
        self.elPlusOneButton.clicked.connect(self.elPlusOneButtonClicked)
        self.elPlusTenButton.clicked.connect(self.elPlusTenButtonClicked)
        self.elMinusPtOneButton.clicked.connect(self.elMinusPtOneButtonClicked)
        self.elMinusOneButton.clicked.connect(self.elMinusOneButtonClicked)
        self.elMinusTenButton.clicked.connect(self.elMinusTenButtonClicked)
        self.elTextBox.returnPressed.connect(self.elTextBoxReturnPressed)

        self.connectButton.clicked.connect(self.connectButtonEvent)
        self.queryButton.clicked.connect(self.queryButtonEvent)
        self.stopButton.clicked.connect(self.stopButtonEvent)
        self.homeButton.clicked.connect(self.homeButtonEvent)
        self.updateButton.clicked.connect(self.updateButtonEvent)
        self.autoQuery_cb.stateChanged.connect(self.catchAutoQueryEvent)

###########################################################################################
	self.syncJoystick_cb.stateChanged.connect(self.catchSyncJoystickEvent)
        QtCore.QObject.connect(self.updateJoystickRefreshTimer, QtCore.SIGNAL('timeout()'), self.refreshJoystickEvent)
        QtCore.QObject.connect(self.update_refresh_rate_le, QtCore.SIGNAL('editingFinished()'), self.updateJoystickRefreshRate)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	self.useJoystick_cb.stateChanged.connect(self.catchUseJoystickEvent)
        QtCore.QObject.connect(self.updateMotorControlTimer, QtCore.SIGNAL('timeout()'), self.sendMotorControlEvent)
        QtCore.QObject.connect(self.update_motor_control_rate_le, QtCore.SIGNAL('editingFinished()'), self.updateMotorControlRate)
###########################################################################################

        QtCore.QObject.connect(self.updateTimer, QtCore.SIGNAL('timeout()'), self.queryButtonEvent)
        QtCore.QObject.connect(self.update_rate_le, QtCore.SIGNAL('editingFinished()'), self.updateRate)
        QtCore.QObject.connect(self.ipAddrTextBox, QtCore.SIGNAL('editingFinished()'), self.updateIPAddress)
        QtCore.QObject.connect(self.portTextBox, QtCore.SIGNAL('editingFinished()'), self.updatePort)

    def updateButtonEvent(self):
        self.updateAzimuth()
        self.updateElevation()

    def homeButtonEvent(self):
        self.tar_az = self.home_az
        self.tar_el = self.home_el
        self.updateAzimuth()
        self.updateElevation()

    def stopButtonEvent(self):
        status, self.cur_az, self.cur_el = self.callback.set_stop()
        if status != -1:
            self.az_compass.set_cur_az(self.cur_az)
            self.el_compass.set_cur_el(self.cur_el)

    def queryButtonEvent(self):
        status, self.cur_az, self.cur_el = self.callback.get_status()
        if status != -1:
            self.az_compass.set_cur_az(self.cur_az)
            self.el_compass.set_cur_el(self.cur_el)
        else:
            self.autoQuery_cb.setCheckState(QtCore.Qt.Unchecked)

###########################################################################################
    def refreshJoystickEvent(self):
        self.refreshJoy()
        #self.progressUD.setValue(self.axisEl)
        #self.progressLR.setValue(self.axisAz)
        #self.progressSpeed.setValue(self.axisSpeed)

        self.progressUD.setValue((self.axisEl + 1)*50)
        self.progressLR.setValue((self.axisAz + 1)*50)
        self.progressSpeed.setValue((self.axisSpeed + 1)*50)

        self.progressUD.show()
        self.progressLR.show()
        self.progressSpeed.show()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def sendMotorControlEvent(self):
        if (self.joy1.get_button(0) == 1): #trigger button held
            self.update_motor_control_rate_le.setStyleSheet("QLineEdit {background-color:rgb(0,255,0); color:rgb(0,0,0);}")
            self.motorSpeed = (self.axisSpeed + 1)*50
            
            #self.callback.set_motor_power(self.motorSpeed, self.motorSpeed)

            self.callback.power_cmd[5] = int(self.motorSpeed)
            self.callback.power_cmd[10] = int(self.motorSpeed)

            self.callback.set_motor_power(int(self.motorSpeed), int(self.motorSpeed))

            self.callback.motor_cmd[1] = 0
            #if self.axisAz > 0:
            #    self.power_cmd[2] += 2
            #elif self.axisAz < 0:
            #    self.power_cmd[2] += 1
            if abs(self.axisAz) > 1e-6:
                self.callback.motor_cmd[1] += 1 + (self.axisAz > 0.0)
            if abs(self.axisEl) > 1e-6:
                self.callback.motor_cmd[1] += 4*(1 + (self.axisEl < 0.0))
            #self.callback.power_cmd[1] = self.callback.motor_cmd[1]
            #self.callback.motor_cmd[5] = self.callback.power_cmd[5]
            #self.callback.motor_cmd[10] = self.callback.power_cmd[10]
            self.callback.sendJoystickValues()

        else:        #trigger button not held
            self.update_motor_control_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,69,0); color:rgb(0,0,0);}")




#H1	self.callback.power_cmd[1]
#---------------------------------
#0	stop motor
#1	left motor 1
#2	right motor 1
#4	up motor 2
#8	down motor 2
#5	left+up
#6	right +up
#9	Down + right
#A	Down + left

            #print "Sending commands..."

###########################################################################################

    def connectButtonEvent(self):
        if (not self.connected):  #Not connected, attempt to connect
            self.connected = self.callback.connect()
            if (self.connected):
                self.connectButton.setText('Disconnect')
                self.net_label.setText("Connected")
                self.net_label.setStyleSheet("QLabel {  font-weight:bold; color:rgb(0,255,0) ; }")
                self.ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
                self.portTextBox.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
                self.ipAddrTextBox.setEnabled(False)
                self.portTextBox.setEnabled(False)
        else:
            self.connected = self.callback.disconnect()
            if (not self.connected):
                self.connectButton.setText('Connect')
                self.net_label.setText("Disconnected")
                self.net_label.setStyleSheet("QLabel {  font-weight:bold; color:rgb(255,0,0) ; }")
                self.ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
                self.portTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
                self.ipAddrTextBox.setEnabled(True)
                self.portTextBox.setEnabled(True)

    def catchAutoQueryEvent(self, state):
        CheckState = (state == QtCore.Qt.Checked)
        if CheckState == True:
            self.updateTimer.start()
            print self.getTimeStampGMT() + "GUI  | Started Auto Update, Interval: " + str(self.update_rate) + " [ms]"
        else:
            self.updateTimer.stop()
            print self.getTimeStampGMT() + "GUI  | Stopped Auto Update"


###########################################################################################
    def catchSyncJoystickEvent(self, state):
        #CheckState = (state == QtCore.Qt.Checked)
        #if CheckState == True:

        if (state == QtCore.Qt.Checked):
            self.updateJoystickRefreshTimer.start()
            print self.getTimeStampGMT() + "GUI  | Started Syncing Joystick, Refresh Rate: " + str(self.update_refresh_rate) + " [ms]"
            self.update_refresh_rate_le.setStyleSheet("QLineEdit {background-color:rgb(0,255,0); color:rgb(0,0,0);}")
        else:
            self.updateJoystickRefreshTimer.stop()
            print self.getTimeStampGMT() + "GUI  | Stopped Syncing Joystick"
            self.update_refresh_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,0,0); color:rgb(0,0,0);}")
            #if (self.useJoystick_cb.checkState() == self.useJoystick_cb.checkState()):
            if (self.useJoystick_cb.checkState() == QtCore.Qt.Checked):
                self.useJoystick_cb.safetyFlag = False

                self.useJoystick_cb.setCheckState(QtCore.Qt.Unchecked)
                print self.getTimeStampGMT() + "GUI  | Joystick Motor Control Halted"
                self.update_motor_control_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,0,0); color:rgb(0,0,0);}")
                self.tar_el = self.cur_el
                self.tar_az = self.cur_az
                self.updateAzimuth()
                self.updateElevation()
                print self.getTimeStampGMT() + "GUI  | Updated Target Position to Current Position"
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def catchUseJoystickEvent(self, state):
        #CheckState = (state == QtCore.Qt.Checked)
        #if CheckState == True:

        if (state == QtCore.Qt.Checked):
            if (self.syncJoystick_cb.checkState() == QtCore.Qt.Checked):
                self.updateMotorControlTimer.start()
                print self.getTimeStampGMT() + "GUI  | Joystick Motor Control Initialized, Motor Control Rate: " + str(self.update_motor_control_rate) + " [ms]"
                self.update_motor_control_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,69,0); color:rgb(0,0,0);}")
            else:
                self.updateMotorControlTimer.stop()
                self.useJoystick_cb.setCheckState (QtCore.Qt.Unchecked)
                self.useJoystick_cb.safetyFlag = True
                #uncheck "Use Joystick"
                print  self.getTimeStampGMT() + "GUI  | ERROR: Sync Joystick Before Initiating Motor Control"
                #print self.useJoystick_cb.checkState()

        elif self.useJoystick_cb.safetyFlag == False:
            self.updateMotorControlTimer.stop()
            print self.getTimeStampGMT() + "GUI  | Joystick Motor Control Halted"
            self.update_motor_control_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,0,0); color:rgb(0,0,0);}")
            self.tar_el = self.cur_el
            self.tar_az = self.cur_az
            self.updateAzimuth()
            self.updateElevation()
            print self.getTimeStampGMT() + "GUI  | Updated Target Position to Current Position"
        else:
            self.useJoystick_cb.safetyFlag = False
###########################################################################################


    def updateRate(self):
        self.update_rate = float(self.update_rate_le.text()) * 1000.0
        self.updateTimer.setInterval(self.update_rate)
        print self.getTimeStampGMT() + "GUI  | Updated Rate Interval to " + str(self.update_rate) + " [ms]"

###########################################################################################
    def updateJoystickRefreshRate(self):
        self.update_refresh_rate = float(self.update_refresh_rate_le.text()) * 1000.0
        self.updateJoystickRefreshTimer.setInterval(self.update_refresh_rate)
        print self.getTimeStampGMT() + "GUI  | Updated Joystick Refresh Rate Interval to " + str(self.update_refresh_rate) + " [ms]"
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def updateMotorControlRate(self):
        self.update_motor_control_rate = float(self.update_motor_control_rate_le.text()) * 1000.0
        self.updateMotorControlTimer.setInterval(self.update_motor_control_rate)
        print self.getTimeStampGMT() + "GUI  | Updated Motor Control Rate Interval to " + str(self.update_motor_control_rate) + " [ms]"
###########################################################################################

    def updateIPAddress(self):
        self.ip = self.ipAddrTextBox.text()

    def updatePort(self):
        self.port = self.portTextBox.text()

    def azTextBoxReturnPressed(self):
        self.tar_az = float(self.azTextBox.text())
        self.updateAzimuth()

    def azPlusPtOneButtonClicked(self):
        self.tar_az = self.tar_az + 0.1
        self.updateAzimuth()

    def azPlusOneButtonClicked(self):
        self.tar_az = self.tar_az + 1
        self.updateAzimuth()

    def azPlusTenButtonClicked(self):
        self.tar_az = self.tar_az + 10
        self.updateAzimuth()

    def azMinusPtOneButtonClicked(self):
        self.tar_az = self.tar_az - 0.1
        self.updateAzimuth()

    def azMinusOneButtonClicked(self):
        self.tar_az = self.tar_az - 1
        self.updateAzimuth()

    def azMinusTenButtonClicked(self):
        self.tar_az = self.tar_az - 10
        self.updateAzimuth()

    def updateAzimuth(self):
        if self.tar_az < -180:
            self.tar_az = -180
            self.azTextBox.setText(str(self.tar_az))
        if self.tar_az > 540:
            self.tar_az = 540
            self.azTextBox.setText(str(self.tar_az))
        self.az_compass.set_tar_az(self.tar_az)
        self.callback.set_position(self.tar_az, self.tar_el)

    def elTextBoxReturnPressed(self):
        self.tar_el = float(self.elTextBox.text())
        self.updateElevation()

    def elPlusPtOneButtonClicked(self):
        self.tar_el = self.tar_el + 0.1
        self.updateElevation()

    def elPlusOneButtonClicked(self):
        self.tar_el = self.tar_el + 1
        self.updateElevation()

    def elPlusTenButtonClicked(self):
        self.tar_el = self.tar_el + 10
        self.updateElevation()

    def elMinusPtOneButtonClicked(self):
        self.tar_el = self.tar_el - 0.1
        self.updateElevation()

    def elMinusOneButtonClicked(self):
        self.tar_el = self.tar_el - 1
        self.updateElevation()

    def elMinusTenButtonClicked(self):
        self.tar_el = self.tar_el - 10
        self.updateElevation()

    def updateElevation(self):
        if self.tar_el < 0:
            self.tar_el = 0
            self.elTextBox.setText(str(self.tar_el))
        if self.tar_el > 180:
            self.tar_el = 180
            self.elTextBox.setText(str(self.tar_el))
        self.el_compass.set_tar_el(self.tar_el)
        self.callback.set_position(self.tar_az, self.tar_el)

    def initNet(self):
        self.ipAddrTextBox = QtGui.QLineEdit()
        self.ipAddrTextBox.setText(self.ip)
        self.ipAddrTextBox.setInputMask("000.000.000.000;")
        self.ipAddrTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        self.ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.ipAddrTextBox.setMaxLength(15)

        self.portTextBox = QtGui.QLineEdit()
        self.portTextBox.setText(str(self.port))
        self.port_validator = QtGui.QIntValidator()
        self.port_validator.setRange(0,65535)
        self.portTextBox.setValidator(self.port_validator)
        self.portTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        self.portTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.portTextBox.setMaxLength(5)
        self.portTextBox.setFixedWidth(50)

        label = QtGui.QLabel('Status:')
        label.setAlignment(QtCore.Qt.AlignRight)
        self.net_label = QtGui.QLabel('Disconnected')
        self.net_label.setAlignment(QtCore.Qt.AlignLeft)
        self.net_label.setFixedWidth(150)

        self.connectButton = QtGui.QPushButton("Connect")
        self.net_label.setStyleSheet("QLabel {font-weight:bold; color:rgb(255,0,0);}")

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.ipAddrTextBox)
        hbox1.addWidget(self.portTextBox)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(label)
        hbox2.addWidget(self.net_label)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addWidget(self.connectButton)
        vbox.addLayout(hbox2)

        self.net_fr.setLayout(vbox)

    def initControls(self):
        self.updateButton = QtGui.QPushButton("Update")
        self.queryButton  = QtGui.QPushButton("Query")
        self.homeButton   = QtGui.QPushButton("Home")
        self.stopButton   = QtGui.QPushButton("STOP!")

        self.autoQuery_cb = QtGui.QCheckBox("Auto Query", self)  #Automatically update ADC voltages checkbox option
        self.autoQuery_cb.setStyleSheet("QCheckBox { font-size: 12px; \
                                                    background-color:rgb(0,0,0); \
                                                    color:rgb(255,255,255); }")

        self.update_rate_le = QtGui.QLineEdit()
        self.update_rate_le.setText("0.25")
        self.update_val = QtGui.QDoubleValidator()
        self.update_rate_le.setValidator(self.update_val)
        self.update_rate_le.setEchoMode(QtGui.QLineEdit.Normal)
        self.update_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.update_rate_le.setMaxLength(4)
        self.update_rate_le.setFixedWidth(50)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.autoQuery_cb)
        hbox1.addWidget(self.update_rate_le)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(self.updateButton)
        hbox2.addWidget(self.queryButton)
        hbox2.addWidget(self.homeButton)

        hbox3 = QtGui.QHBoxLayout()
        hbox3.addWidget(self.stopButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.button_fr.setLayout(vbox)

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.setInterval(self.update_rate)

    def initMotorCtrl(self):
        self.UpLeftButton = QtGui.QPushButton("U+L")
        self.UpButton = QtGui.QPushButton("Up")
        self.UpRightButton = QtGui.QPushButton("U+R")
        self.LeftButton = QtGui.QPushButton("Left")
        self.StopButton = QtGui.QPushButton("STOP!")
        self.RightButton = QtGui.QPushButton("Right")
        self.DnLeftButton = QtGui.QPushButton("D+L")
        self.DownButton = QtGui.QPushButton("Down")
        self.DnRightButton = QtGui.QPushButton("D+R")
	self.JoystickBox = QtGui.QCheckBox("Use Joystick", self)
	self.JoystickBox.setStyleSheet("QCheckBox {font-size: 13px;\
						background-color:rgb(0,0,0);\
						color:rgb(255,255,255);}")

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox3 = QtGui.QHBoxLayout()
	hbox4 = QtGui.QHBoxLayout()

        hbox1.addWidget(self.UpLeftButton)
        hbox1.addWidget(self.UpButton)
        hbox1.addWidget(self.UpRightButton)

        hbox2.addWidget(self.LeftButton)
        hbox2.addWidget(self.StopButton)
        hbox2.addWidget(self.RightButton)

        hbox3.addWidget(self.DnLeftButton)
        hbox3.addWidget(self.DownButton)
        hbox3.addWidget(self.DnRightButton)

	hbox4.addWidget(self.JoystickBox)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
	vbox.addLayout(hbox4)

        self.ctrl_fr.setLayout(vbox)

    def initElevation(self):
        self.el_compass = el_QwtDial(self.el_fr)
        x = 172; y = 350; w = 50; s = 4; h = 25
        self.elPlusPtOneButton = QtGui.QPushButton(self.el_fr)
        self.elPlusPtOneButton.setText("+0.1")
        self.elPlusPtOneButton.setGeometry(x,y,w,h)

        self.elPlusOneButton = QtGui.QPushButton(self.el_fr)
        self.elPlusOneButton.setText("+1.0")
        self.elPlusOneButton.setGeometry(x+s+w,y,w,h)

        self.elPlusTenButton = QtGui.QPushButton(self.el_fr)
        self.elPlusTenButton.setText("+10.0")
        self.elPlusTenButton.setGeometry(x+(2*s)+(2*w),y,w,h)

        self.elMinusPtOneButton = QtGui.QPushButton(self.el_fr)
        self.elMinusPtOneButton.setText("-0.1")
        self.elMinusPtOneButton.setGeometry(x-s-w,y,w,h)

        self.elMinusOneButton = QtGui.QPushButton(self.el_fr)
        self.elMinusOneButton.setText("-1.0")
        self.elMinusOneButton.setGeometry(x-(2*s)-(2*w),y,w,h)

        self.elMinusTenButton = QtGui.QPushButton(self.el_fr)
        self.elMinusTenButton.setText("-10.0")
        self.elMinusTenButton.setGeometry(x-(3*s)-(3*w),y,w,h)

        self.elTextBox = QtGui.QLineEdit(self.el_fr)
        self.elTextBox.setText("000.0")
        self.elTextBox.setInputMask("000.0;")
        self.elTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        self.elTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.elTextBox.setMaxLength(6)
        self.elTextBox.setGeometry(140,320,60,25)

    def initAzimuth(self):
        #geo = self.az_fr.frameRect()
        #print geo.x, geo.y, geo.width, geo.height
        self.az_compass = az_QwtDial(self.az_fr)
        x = 172; y = 350; w = 50; s = 4; h = 25
        self.azPlusPtOneButton = QtGui.QPushButton(self.az_fr)
        self.azPlusPtOneButton.setText("+0.1")
        self.azPlusPtOneButton.setGeometry(x,y,w,h)

        self.azPlusOneButton = QtGui.QPushButton(self.az_fr)
        self.azPlusOneButton.setText("+1.0")
        self.azPlusOneButton.setGeometry(x+s+w,y,w,h)

        self.azPlusTenButton = QtGui.QPushButton(self.az_fr)
        self.azPlusTenButton.setText("+10.0")
        self.azPlusTenButton.setGeometry(x+(2*s)+(2*w),y,w,h)

        self.azMinusPtOneButton = QtGui.QPushButton(self.az_fr)
        self.azMinusPtOneButton.setText("-0.1")
        self.azMinusPtOneButton.setGeometry(x-s-w,y,w,h)

        self.azMinusOneButton = QtGui.QPushButton(self.az_fr)
        self.azMinusOneButton.setText("-1.0")
        self.azMinusOneButton.setGeometry(x-(2*s)-(2*w),y,w,h)

        self.azMinusTenButton = QtGui.QPushButton(self.az_fr)
        self.azMinusTenButton.setText("-10.0")
        self.azMinusTenButton.setGeometry(x-(3*s)-(3*w),y,w,h)

        self.azTextBox = QtGui.QLineEdit(self.az_fr)
        self.azTextBox.setText("180.0")
        self.azTextBox.setInputMask("#000.0;")
        self.azTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        self.azTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.azTextBox.setMaxLength(6)
        self.azTextBox.setGeometry(140,320,60,25)

    def initFrames(self):
        self.az_fr = QtGui.QFrame(self)
        self.az_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.az_fr.setFixedWidth(340)
        self.az_fr.setFixedHeight(380)

        self.el_fr = QtGui.QFrame(self)
        self.el_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.el_fr.setFixedWidth(340)
        self.el_fr.setFixedHeight(380)

        self.button_fr = QtGui.QFrame(self)
        self.button_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.button_fr.setFixedWidth(250)
        self.button_fr.setFixedHeight(100)

        self.ctrl_fr = QtGui.QFrame(self)
        self.ctrl_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.ctrl_fr.setFixedWidth(220)
        self.ctrl_fr.setFixedHeight(100)

        self.net_fr = QtGui.QFrame(self)
        self.net_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.net_fr.setFixedWidth(200)
        self.net_fr.setFixedHeight(100)

	self.progress_fr = QtGui.QFrame(self)
	self.progress_fr.setFrameShape(QtGui.QFrame.StyledPanel)
	self.progress_fr.setFixedWidth(680)
	self.progress_fr.setFixedHeight(140)

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
	hbox4 = QtGui.QHBoxLayout()

        hbox1.addWidget(self.az_fr)
        hbox1.addWidget(self.el_fr)

        hbox2.addWidget(self.net_fr)
        hbox2.addWidget(self.ctrl_fr)
        hbox2.addWidget(self.button_fr)

	hbox4.addWidget(self.progress_fr)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
	vbox.addLayout(hbox4)

        self.setLayout(vbox)

    def initJoystick(self):
###########################################################################################
        self.syncJoystick_cb = QtGui.QCheckBox("Sync Joystick | Refresh Rate (sec)", self)  #Automatically update ADC voltages checkbox option
        self.syncJoystick_cb.setStyleSheet("QCheckBox { font-size: 12px; \
                                                    background-color:rgb(0,0,0); \
                                                    color:rgb(255,255,255); }")
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.useJoystick_cb = QtGui.QCheckBox("Use Joystick   | Refresh Rate (sec)", self)  #Automatically update ADC voltages checkbox option
        self.useJoystick_cb.setStyleSheet("QCheckBox { font-size: 12px; \
                                                    background-color:rgb(0,0,0); \
                                                    color:rgb(255,255,255); }")
        self.useJoystick_cb.safetyFlag = False
###########################################################################################
	
        self.axisAz = 0
	self.axisEl = 0
	self.axisSpeed = 0

        self.progressUD = QtGui.QProgressBar()
	self.progressLR = QtGui.QProgressBar()
	self.progressSpeed = QtGui.QProgressBar()

	self.progressUD.setRange(0, 100)
	self.progressLR.setRange(0, 100)
	self.progressSpeed.setRange(0, 100)

	self.progressLRText = QtGui.QLabel("LEFT-RIGHT")
	self.progressUDText = QtGui.QLabel("UP-DOWN")
	self.progressSpText = QtGui.QLabel("SPEED")

	self.progressUDText.setAlignment(QtCore.Qt.AlignRight)
	self.progressLRText.setAlignment(QtCore.Qt.AlignRight)
	self.progressSpText.setAlignment(QtCore.Qt.AlignRight)
	self.progressUDText.setFixedWidth(80)
	self.progressLRText.setFixedWidth(80)
	self.progressSpText.setFixedWidth(80)

###########################################################################################
        self.update_refresh_rate_le = QtGui.QLineEdit()
        self.update_refresh_rate_le.setText(str(self.update_refresh_rate/1000.0))
        self.update_val = QtGui.QDoubleValidator()
        self.update_refresh_rate_le.setValidator(self.update_val)
        self.update_refresh_rate_le.setEchoMode(QtGui.QLineEdit.Normal)
        self.update_refresh_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,0,0); color:rgb(0,0,0);}")
        self.update_refresh_rate_le.setMaxLength(4)
        self.update_refresh_rate_le.setFixedWidth(50)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.update_motor_control_rate_le = QtGui.QLineEdit()
        self.update_motor_control_rate_le.setText(str(self.update_motor_control_rate/1000.0))
        self.update_val = QtGui.QDoubleValidator()
        self.update_motor_control_rate_le.setValidator(self.update_val)
        self.update_motor_control_rate_le.setEchoMode(QtGui.QLineEdit.Normal)
        
        self.update_motor_control_rate_le.setStyleSheet("QLineEdit {background-color:rgb(255,0,0); color:rgb(0,0,0);}")
        self.update_motor_control_rate_le.setMaxLength(4)
        self.update_motor_control_rate_le.setFixedWidth(50)
###########################################################################################

	vbox = QtGui.QVBoxLayout()
	hbox1 = QtGui.QHBoxLayout()
	hbox2 = QtGui.QHBoxLayout()
	hbox3 = QtGui.QHBoxLayout()
        hboxLabel = QtGui.QHBoxLayout()

###########################################################################################
        hbox4 = QtGui.QHBoxLayout()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        hbox5 = QtGui.QHBoxLayout()
###########################################################################################

	hbox1.addWidget(self.progressUDText)
	hbox1.addWidget(self.progressUD)
	hbox2.addWidget(self.progressLRText)
	hbox2.addWidget(self.progressLR)
	hbox3.addWidget(self.progressSpText)
	hbox3.addWidget(self.progressSpeed)

        self.refreshLabel = QtGui.QLabel("Refresh Rate (sec)")
        self.refreshLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        hboxLabel.addWidget(self.refreshLabel)
###########################################################################################
        hbox4.addWidget(self.syncJoystick_cb)
        hbox4.addWidget(self.update_refresh_rate_le)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        hbox5.addWidget(self.useJoystick_cb)
        hbox5.addWidget(self.update_motor_control_rate_le)
###########################################################################################

	vbox.addLayout(hbox1)
	vbox.addLayout(hbox2)
	vbox.addLayout(hbox3)

        vbox.addLayout(hboxLabel)

###########################################################################################
        vbox.addLayout(hbox4)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        vbox.addLayout(hbox5)
###########################################################################################

	self.progress_fr.setLayout(vbox)

        self.updateJoystickRefreshTimer = QtCore.QTimer(self)
        self.updateJoystickRefreshTimer.setInterval(self.update_refresh_rate)


        self.updateMotorControlTimer = QtCore.QTimer(self)
        self.updateMotorControlTimer.setInterval(self.update_motor_control_rate)

    def darken(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.black)
        palette.setColor(QtGui.QPalette.WindowText,QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text,QtCore.Qt.white)
        self.setPalette(palette)

    def getTimeStampGMT(self):
        return str(date.utcnow()) + " GMT | "

