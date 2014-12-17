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
import sys


def mode_Motor(myQ):

    logger = logging.getLogger('myQ.mode_Motor')
    cycleTime = 0.010  # [s]

    usedMotor = 0

    try:

        #wait ack from user to start motors
        while myQ.rc.command != 9 and myQ.rc.command != -1 and myQ.rc.cycling:
            pass
        if myQ.rc.command != -1:
            myQ.rc.command = 0
            myQ.rc.throttle = 0

        initTime = time()
        previousTime = initTime
        currentTime = initTime

        counterPerf = 0  # used for performance tests
        #displayCommand()
        while myQ.rc.cycling is True and myQ.rc.command != -1 and myQ.netscan.connectionUp is True:
            #manage cycletime
            while currentTime <= (previousTime + cycleTime):
                currentTime = time()
                sleep(0.0001)
            previousTime = currentTime

            # user commands:
            if myQ.rc.command == 0 and usedMotor != 0:
                usedMotor = 0
                myQ.rc.throttle = 0  # when switch between motors > reset throttle
            elif myQ.rc.command == 1 and usedMotor != 1:
                usedMotor = 1
                myQ.rc.throttle = 0
            elif myQ.rc.command == 2 and usedMotor != 2:
                usedMotor = 2
                myQ.rc.throttle = 0
            elif  myQ.rc.command == 3 and usedMotor != 3:
                usedMotor = 3
                myQ.rc.throttle = 0

            myQ.motor[usedMotor].setW(myQ.rc.throttle)

            myQ.writeLog(currentTime - initTime)

            #used for performance test only
            doPerf = False
            if doPerf is True:
                counterPerf += 1
                if  counterPerf == 1000:
                    logger.debug('MODE-MOTOR 1000 cycles time:' + str(initTime - currentTime))

    except:
        logger.critical('Unexpected error:', sys.exc_info()[0])