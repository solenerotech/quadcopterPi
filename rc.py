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

import curses
import threading
import logging


class rc(threading.Thread):

#here i can manage the remote control as a webserver or in a parallel thread
    def __init__(self, screen, throttle=0, roll=0, pitch=0, yaw=0):

        self.logger = logging.getLogger('myQ.rc')
        threading.Thread.__init__(self)
        self.screen = screen

        self.throttle = throttle
        self.throttleMin = 0
        self.throttleMax = 100

        self.roll = roll
        self.rollMin = -25
        self.rollMax = 25

        self.pitch = pitch
        self.pitchMin = -5
        self.pitchMax = 5

        self.yaw = yaw
        self.yawMin = -5
        self.yawMax = 5

        self.cycling = True
        self.command = -1

#TODO add  setup() function for setting the min/max values, instead of put all in the init()
#TODO use self.Joystick  instead of angles , in order to have a variable behaviour

    def run(self):

        self.logger.debug('RC running...')
        while self.cycling:

            #TODO add also command for pitch , yaw , and hover save and hover set
            #this is for not processing all the buffer,
            #but a command per cycle
            curses.flushinp()
            #timeout in millis
            #TODO verify if this is necessary
            self.screen.timeout(100)
            #getch returns -1 if timeout
            res = self.screen.getch()
            if res == 32:  # 32 =SPACEBAR
                self.cycling = False
            else:
                if res == ord('0'):
                    self.command = 0
                elif res == ord('1'):
                    self.command = 1
                elif res == ord('2'):
                    self.command = 2
                elif res == ord('3'):
                    self.command = 3
                elif res == ord('4'):
                    self.command = 4
                elif res == ord('5'):
                    self.command = 5
                elif res == ord('6'):
                    self.command = 6
                elif res == ord('7'):
                    self.command = 7
                elif res == ord('8'):
                    self.command = 8
                elif res == ord('9'):
                    self.command = 9
                elif res == ord('a'):
                    self.roll = self.roll + 1
                elif res == ord('z'):
                    self.roll = self.roll - 1
                elif res == ord('m'):
                    self.pitch = self.pitch + 1
                elif res == ord('n'):
                    self.pitch = self.pitch - 1
                #TODO add yaw
                elif res == ord('t'):
                    self.throttle = self.throttle + 1
                elif res == ord('f'):
                    self.throttle = self.throttle - 1

                if self.throttle < self.throttleMin:
                    self.throttle = self.throttleMin
                elif self.throttle > self.throttleMax:
                    self.throttle = self.throttleMax

                if self.roll < self.rollMin:
                    self.roll = self.rollMin
                elif self.roll > self.rollMax:
                    self.roll = self.rollMax
                if self.pitch < self.pitchMin:
                    self.pitch = self.pitchMin
                elif self.pitch > self.pitchMax:
                    self.pitch = self.pitchMax
                if self.yaw < self.yawMin:
                    self.yaw = self.yawMin
                elif self.yaw > self.yawMax:
                    self.yaw = self.yawMax

    def stop(self):
        self.logger.debug('RC stopping...')

