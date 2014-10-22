############################################################################
#
#    QuadcopeRPI- SW for controlling a quadcopter by RPI
#
#    Copyright (C) 2014 Oscar Ferrato (solenero tech)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#    Contact me at:
#    solenero.tech@gmail.com
#    solenerotech.wordpress.com
##############################################################################

#2013.08.06 rpi test2
#added User Interface
#added Quadcopter.py

#2013.08.13 added pid.py
#2013.08.18  added thread in rpycontrol.py
#2013.08.18  added angle class
#2014.10.1 added netscan
#2014.10.14 added load and save  function
#2014.10.18 moved the screen directly inside quadcopter
#TODO verificare perche l'imput adesso e' immediato e non attende piu un tot...

import logging
from pid import pid
from sensor import sensor
from motor import motor
from rc import rc
from netscan import netscan
from prop import prop
from display import display


class quadcopter(object):

    def __init__(self, name, pin0=18, pin1=23, pin2=24, pin3=25, simulation=True):

#GPIO: 18 23 24 25
#pin : 12 16 18 22

        self.logger = logging.getLogger('myQ.quadcopter')
        self.name = name
        self.simulation = simulation

        self.motor = [motor('M' + str(i), 0) for i in xrange(4)]
        self.motor[0] = motor('M0', pin0, kv=1000, WMin=0, WMax=100, simulation=self.simulation)
        self.motor[1] = motor('M1', pin1, kv=1000, WMin=0, WMax=100, simulation=self.simulation)
        self.motor[2] = motor('M2', pin2, kv=1000, WMin=0, WMax=100, simulation=self.simulation)
        self.motor[3] = motor('M3', pin3, kv=1000, WMin=0, WMax=100, simulation=self.simulation)

        self.sensor = sensor()

        self.display = display(self)

        self.rc = rc(self.display.screen)

        self.pidR = pid()
        self.pidP = pid()
        self.pidY = pid()
        self.pidR_rate = pid()
        self.pidP_rate = pid()
        self.pidY_rate = pid()
        self.ip = '192.168.0.3'

        self.netscan = netscan(self.ip)

        self.savelog = False
        self.calibIMU = False
        self.debuglev = 0
        self.netscanning = False

        #for quadricopter phisics calculations- not used yet
        self.prop = prop(9, 4.7, 1)
        self.voltage = 12  # [V]
        self.mass = 2  # [Kg]
        self.barLenght = 0.23  # [mm]
        self.barMass = 0.15  # [kg]

    def load(self, file_name):
        try:
            with open(file_name, 'r') as cfg_file:
                ver = self.getInt(cfg_file)
                if ver is not 1:
                    self.logger.critical('cfg file not compatible: need version 1')
                self.ip = self.getStr(cfg_file)
                self.motor[0].pin = self.getInt(cfg_file)
                self.motor[1].pin = self.getInt(cfg_file)
                self.motor[2].pin = self.getInt(cfg_file)
                self.motor[3].pin = self.getInt(cfg_file)
                cfg_file.flush()

        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, file_name)

    def getStr(self, cfg_file):
        strg = cfg_file.readline()
        while strg[0] == '#':
            self.logger.debug('Loading comment %s ', strg)
            strg = cfg_file.readline()
        strg = strg.split('=')
        self.logger.debug('Loading data %s ', strg[1])
        return strg[1]

    def getInt(self, cfg_file):
        strg = cfg_file.readline()
        while strg[0] == '#':
            self.logger.debug('Loading comment %s ', strg)
            strg = cfg_file.readline()
        strg = strg.split('=')
        self.logger.debug('Loading data %d ', int(strg[1]))
        return int(strg[1])

    def save(self, file_name):

        #remember to use ''PARAM_NAME' + '='
        try:
            with open(file_name, 'w+') as cfg_file:
                cfg_file.write('ver=1')
                cfg_file.write('IP=%s\n' % self.ip)  # example for string
                cfg_file.write('M0=%d\n' % self.motor[0].pin)
                cfg_file.write('M1=%d\n' % self.motor[1].pin)
                cfg_file.write('M2=%d\n' % self.motor[2].pin)
                cfg_file.write('M3=%d\n' % self.motor[3].pin)
                cfg_file.flush()

        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, file_name)

    def start(self):
        "start  all motors,sensor,rc"

        self.sensor.start()
        self.display.start()
        self.rc.start()
        self.netscan.start()
        #Init motors
        for i in xrange(4):
            self.motor[i].start()
            self.motor[i].setW(0)
            #sleep(1) # used to ear clearly all motor beep status

    def stop(self):
        "stop all motors,sensor,rc"

        self.display.stop()

        for i in xrange(4):
            self.motor[i].stop()

        self.netscan.stop()
        self.sensor.stop()
        self.rc.stop()

    def saveWh(self):
        "set Wh all motors"

        #TODO not used . Remove it
        for i in xrange(4):
            self.motor[i].saveWh()