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

#2013.08.09 new naming
#RPM>W
#RPMEquil>Wh (h=hover)
#simulation > powered
#mId > name

#2013.09.06
#powered >simulation
#add powered = the PWM signal is out

#2014.02.20
#simplified code removing unused functions
#add dma_channel=1, subcycle_time_us=5000, pulse_incr_us=1 for better accuracy

#2014.06.20
#switch from pwm.setservo()  to PWM.add_channel_pulse() to avoid unstable
# motor speed

#2014.09.20
#added logging

from time import sleep
import logging


class motor(object):
    """Manages the currect Angular rotation W
    Implements the IO interface using the RPIO lib
    __init_(self, name, pin, kv=1000, WMin=1, WMax=100, debug=True, simulation=True):
    More info on RPIO in http://pythonhosted.org/RPIO/index.html"""

    def __init__(self, name, pin, kv=1000, WMin=0, WMax=100, debug=True, simulation=True):
        self.logger = logging.getLogger('myQ.motor')
        self.name = name
        self.powered = False
        self.simulation = simulation
        self.pin = pin
        self.debug = debug
        self.__WMin = 0
        self.__WMax = 100
        self.setWLimits(WMin, WMax)

        self.__W = self.__WMin
        self.__Wh = 10

        self.kv = kv
        self.mass = 0.050  # [kg]

        try:
            from RPIO import PWM
            #here just check that library is available
            self.PWM = PWM
        except ImportError, strerror:
            self.simulation = True
            self.logger.error('Error: Motor NOT initiazized. %s', strerror)

    def setWLimits(self, WMin, WMax):
        "set the pin for each motor"
        if WMin < 0:
            WMin = 0
        self.__WMin = WMin
        if WMax > 100:
            WMax = 100
        self.__WMax = WMax

    def saveWh(self):
        "Save Wh = current W%"
        #TODO not used . Remove it
        self.__Wh = self.__W

    def setWh(self):
        "Sets current W% =Wh"
        #TODO not used . Remove it
        self.__W = self.__Wh
        self.setW(self.__W)

    def getWh(self):
        "returns current W% =Wh"
        #TODO not used . Remove it
        return self.__Wh

    def start(self):
        "Run the procedure to init the PWM"
        if self.simulation is False:
            try:
                from RPIO import PWM
                if not self.PWM.is_setup():
                    self.PWM.setup(pulse_incr_us=1)
                    self.PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
                    self.PWM.init_channel(1, 3000)
                #self.servo = PWM.Servo(dma_channel=1, subcycle_time_us=5000,pulse_incr_us=1)
                self.powered = True
                self.logger.debug('Motor %s started', self.name)

            except ImportError:
                self.logger.critical('Failed to init RPIO...')
                self.simulation = True
                self.powered = False

    def stop(self):
        "Stop PWM signal"

        self.setW(0)
        sleep(0.1)
        if self.powered:
            self.PWM.add_channel_pulse(1, self.pin, 0, 1000)
            #self.servo.stop_servo(self.pin)
            self.powered = False
        self.logger.debug('Motor %s stopped', self.name)

    def getW(self):
        "retuns current W%"
        return self.__W

    def setW(self, W):
        "Checks W% is between limits than sets it"

        PW = 0
        self.__W = round(W, 1)
        #W is rounded to the first decimal, since PWM has pulse increment=1us
        if self.__W < self.__WMin:
            self.__W = self.__WMin
        if self.__W > self.__WMax:
            self.__W = self.__WMax
        PW = int(1000 + (self.__W) * 10)
        # Set servo to xxx us ,nanosec
        if self.powered:
            #self.servo.set_servo(self.pin, PW)
            self.PWM.add_channel_pulse(1, self.pin, 0, PW)