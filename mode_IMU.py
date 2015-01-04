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


def mode_IMU(myQ):

    logger = logging.getLogger('myQ.mode_IMU')

    cycleTime = 0.1  # [s]

    try:

        initTime = time()
        previousTime = initTime
        currentTime = initTime

        while myQ.rc.cycling is True and myQ.rc.command != -1 and myQ.netscan.connectionUp is True:

            #manage cycletime
            while currentTime <= previousTime + cycleTime:
                currentTime = time()
                sleep(0.001)
            previousTime = currentTime

            # user commands:
            if myQ.rc.command == 1:
                #basic calibration
                myQ.sensor.calibrate()
                myQ.rc.command = -1
            elif myQ.rc.command == 3:
                #fine calibration, first measurament
                myQ.sensor.calibrate()
                myQ.rc.command = 4
            elif myQ.rc.command == 5:
                #fine calibration, second measurament,with drone rotated 180' respect yaw
                myQ.sensor.calibrate(fine=True)
                myQ.rc.command = -1

    except:
        logger.critical('Unexpected error:', sys.exc_info()[0])