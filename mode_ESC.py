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

#2014.10.23

from time import time, sleep
import logging


def mode_ESC(myQ):

    logger = logging.getLogger('myQ.mode_ESC')

    cycleTime = 0.010  # [s]


    try:

        #wait ack from user to start motors
        while myQ.rc.command != 9 and myQ.rc.command != -1 and myQ.rc.cycling:
            pass
        if myQ.rc.command != -1:
            myQ.rc.throttle = 0
            usedMotor = -1

        initTime = time()
        previousTime = initTime
        currentTime = initTime

        #displayCommand()
        while myQ.rc.cycling is True and myQ.rc.command != -1:

            #manage cycletime
            while currentTime <= previousTime + cycleTime:
                currentTime = time()
                sleep(0.001)
            previousTime = currentTime


            # user commands:
            if myQ.rc.command == 0 and usedMotor != 0:
                usedMotor = 0
            elif myQ.rc.command == 1 and usedMotor != 1:
                usedMotor = 1
            elif myQ.rc.command == 2 and usedMotor != 2:
                usedMotor = 2
            elif  myQ.rc.command == 3 and usedMotor != 3:
                usedMotor = 3

            if usedMotor > -1 and usedMotor < 4:
                #wait ack to set max Throttle
                while myQ.rc.command != 5 and myQ.rc.command != -1 and myQ.rc.cycling:
                    pass
                myQ.motor[usedMotor].setW(100)
                sleep(5)
                #wait ack to reset  Throttle
                while myQ.rc.command != 6 and myQ.rc.command != -1 and myQ.rc.cycling:
                    pass
                myQ.motor[usedMotor].setW(0)
                myQ.rc.command = -1

    finally:
        try:
            if myQ.savelog:
                with open('myQ.csv', 'w+') as data_file:
                    data_file.write(datalog)
                    data_file.flush()
        except IOError, err:
            logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'myQ.csv')
