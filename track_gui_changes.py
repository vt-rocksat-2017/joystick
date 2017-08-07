    def connectSignals(self):
#        self.autoQuery_cb.stateChanged.connect(self.catchAutoQueryEvent)
        self.useJoystick_cb.stateChanged.connect(self.catchUseJoystickEvent)

#    def catchAutoQueryEvent(self, state):
#        CheckState = (state == QtCore.Qt.Checked)
#        if CheckState == True:
#            self.updateTimer.start()
#            print self.getTimeStampGMT() + "GUI  | Started Auto Update, Interval: " + str(self.update_rate) + " [ms]"
#        else:
#            self.updateTimer.stop()
#            print self.getTimeStampGMT() + "GUI  | Stopped Auto Update"

    def catchUseJoystickEvent(self, state):
        CheckState = (state == QtCore.Qt.Checked)
        if CheckState == True:
            self.joystickRefreshTimer.start()
            print self.getTimeStampGMT() + "GUI  | Started Using Joystick, Refresh Rate: " + str(self.update_rate) + " [ms]"
        else:
            self.joystickRefreshTimer.stop()
            print self.getTimeStampGMT() + "GUI  | Stopped Using Joystick"




    def updateRate(self):
        self.update_rate = float(self.update_rate_le.text()) * 1000.0
        self.updateTimer.setInterval(self.update_rate)
        print self.getTimeStampGMT() + "GUI  | Updated Rate Interval to " + str(self.update_rate) + " [ms]"




    def initControls(self):

#        self.autoQuery_cb = QtGui.QCheckBox("Auto Query", self)  #Automatically update ADC voltages checkbox option
#        self.autoQuery_cb.setStyleSheet("QCheckBox { font-size: 12px; \
#                                                    background-color:rgb(0,0,0); \
#                                                    color:rgb(255,255,255); }")
        self.useJoystick_cb = QtGui.QCheckBox("Use Joystick", self)  #Automatically update ADC voltages checkbox option
        self.useJoystick_cb.setStyleSheet("QCheckBox { font-size: 12px; \
                                                    background-color:rgb(0,0,0); \
                                                    color:rgb(255,255,255); }")

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

        #self.button_fr.setLayout(vbox)

        #self.updateTimer = QtCore.QTimer(self)
        #self.updateTimer.setInterval(self.update_rate)

        self.joystickRefreshTimer = QtCore.QTimer(self)
        self.joystickRefreshTimer.setInterval(self.update_rate)




    def initJoystick(self):
        self.useJoystick_cb = QtGui.QCheckBox("Use Joystick", self)  #Automatically update ADC voltages checkbox option
        self.useJoystick_cb.setStyleSheet("QCheckBox { font-size: 12px; \
                                                    background-color:rgb(0,0,0); \
                                                    color:rgb(255,255,255); }")
#	self.progressUD = QtGui.QProgressBar()
#	self.progressLR = QtGui.QProgressBar()
#	self.progressSpeed = QtGui.QProgressBar()

#	self.progressUD.setRange(-1, 1)
#	self.progressLR.setRange(-1, 1)
#	self.progressSpeed.setRange(-1, 1)

#	self.progressLRText = QtGui.QLabel("LEFT-RIGHT")
#	self.progressUDText = QtGui.QLabel("UP-DOWN")
#	self.progressSpText = QtGui.QLabel("SPEED")

#	self.progressUDText.setAlignment(QtCore.Qt.AlignRight)
#	self.progressLRText.setAlignment(QtCore.Qt.AlignRight)
#	self.progressSpText.setAlignment(QtCore.Qt.AlignRight)
#	self.progressUDText.setFixedWidth(80)
#	self.progressLRText.setFixedWidth(80)
#	self.progressSpText.setFixedWidth(80)

#	vbox = QtGui.QVBoxLayout()
#	hbox1 = QtGui.QHBoxLayout()
#	hbox2 = QtGui.QHBoxLayout()
#	hbox3 = QtGui.QHBoxLayout()

#	hbox1.addWidget(self.progressUDText)
#	hbox1.addWidget(self.progressUD)
#	hbox2.addWidget(self.progressLRText)
#	hbox2.addWidget(self.progressLR)
#	hbox3.addWidget(self.progressSpText)
#	hbox3.addWidget(self.progressSpeed)

        hbox4.addWidget(self.useJoystick_cb)

#	vbox.addLayout(hbox1)
#	vbox.addLayout(hbox2)
#	vbox.addLayout(hbox3)

        vbox.addLayout(hbox4)
        
	self.progress_fr.setLayout(vbox)

