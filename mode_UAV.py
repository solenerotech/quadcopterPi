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

#2014.10.21

from time import time, sleep
import logging
import sys


def mode_UAV(myQ):

    logger = logging.getLogger('myQ.mode_UAV')

    cycleTime = 0.010  # [s]

    corrR = 0
    corrP = 0
    corrY = 0
    roll_rate_target = 0
    pitch_rate_target = 0

    myQ.rc.throttle = 0

    selectedPath = 0

    try:

        #wait ack from user to start motors
        while myQ.rc.command != 9 and myQ.rc.command != -1 and myQ.rc.cycling:
            pass

        if myQ.rc.command != -1:
            myQ.rc.command = 0

        initTime = time()
        previousTime = initTime
        currentTime = initTime

        #displayCommand()
        while myQ.rc.cycling is True and myQ.rc.command != -1:

            #manage cycletime
            while currentTime <= previousTime + cycleTime:
                currentTime = time()
                sleep(0.001)
            stepTime = currentTime - previousTime
            previousTime = currentTime

            # user commands:
            if myQ.rc.command == 0:
                corrR = 0
                corrP = 0
            elif myQ.rc.command == 1:
                #included 2 incapsulated pid for each angle:
                #1) get the Wcorr as roll PID
                #2) divide it for the cycletime to get a rot speed (target roll_rate)
                #3) get the Wcorr as roll_rate PID

                #ROLL
                roll_rate_target = myQ.pidR.calc(myQ.rc.roll, myQ.sensor.roll, stepTime)
                roll_rate_target = roll_rate_target / stepTime
                #now using r_rate from gyro . it is more claen signal
                corrR = myQ.pidR_rate.calc(roll_rate_target, myQ.sensor.r_rate, stepTime)

                #PITCH
                pitch_rate_target = myQ.pidP.calc(myQ.rc.pitch, myQ.sensor.pitch, stepTime)
                pitch_rate_target = pitch_rate_target / stepTime

                #now using r_rate from gyro . it is more claen signal
                corrP = myQ.pidP_rate.calc(pitch_rate_target, myQ.sensor.p_rate, stepTime)

                #TODO comment below to activate pitch
                #corrP = 0

            elif myQ.rc.command > 1:
                selectedPath = myQ.rc.command
                pathTime = time()
                myQ.rc.command = 1

            #TODO add yaw pid control here and throttle pid control

            #The sign used to add the correction depends on the
            # motor position respect the IMU orientation
            myQ.motor[0].setW(myQ.rc.throttle + corrR)
            myQ.motor[2].setW(myQ.rc.throttle - corrR)

            #myQ.motor[1].setW(myQ.rc.throttle - corrP)
            #myQ.motor[3].setW(myQ.rc.throttle + corrP)

            if  selectedPath == 2:
                #Test to have delta roll target in fiexd time

                if currentTime - pathTime > 3 and currentTime - pathTime < 6:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 6 and currentTime - pathTime < 9:
                    myQ.rc.roll = 0
                if currentTime - pathTime > 9 and currentTime - pathTime < 12:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 12 and currentTime - pathTime < 15:
                    myQ.rc.roll = 0
                if currentTime - pathTime > 15 and currentTime - pathTime < 18:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 18:
                    myQ.rc.roll = 0

            if  selectedPath == 3:
                #Test to have delta roll target in fiexd time

                if currentTime - pathTime > 3 and currentTime - pathTime < 6:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 6 and currentTime - pathTime < 9:
                    myQ.rc.roll = -3
                if currentTime - pathTime > 9 and currentTime - pathTime < 12:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 12 and currentTime - pathTime < 15:
                    myQ.rc.roll = -3
                if currentTime - pathTime > 15 and currentTime - pathTime < 18:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 18:
                    myQ.rc.roll = 0

            if  selectedPath == 4:
                #Test to have delta roll target in fiexd time

                if currentTime - pathTime > 2 and currentTime - pathTime < 3:
                    myQ.rc.roll = 1
                if currentTime - pathTime > 3 and currentTime - pathTime < 4:
                    myQ.rc.roll = 2
                if currentTime - pathTime > 4 and currentTime - pathTime < 5:
                    myQ.rc.roll = 3
                if currentTime - pathTime > 5 and currentTime - pathTime < 6:
                    myQ.rc.roll = 0
                if currentTime - pathTime > 6 and currentTime - pathTime < 7:
                    myQ.rc.roll = 1
                if currentTime - pathTime > 7 and currentTime - pathTime < 8:
                    myQ.rc.roll = 0
                if currentTime - pathTime > 8 and currentTime - pathTime < 9:
                    myQ.rc.roll = 1
                if currentTime - pathTime > 9 and currentTime - pathTime < 12:
                    myQ.rc.roll = 0
                if currentTime - pathTime > 12 and currentTime - pathTime < 15:
                    myQ.rc.roll = 5
                if currentTime - pathTime > 15 and currentTime - pathTime < 18:
                    myQ.rc.roll = 0
                if currentTime - pathTime > 18 and currentTime - pathTime < 20:
                    myQ.rc.roll = -5
                if currentTime - pathTime > 20:
                    myQ.rc.roll = 0

            myQ.writeLog(currentTime - initTime)

    except:
        logger.critical('Unexpected error:', sys.exc_info()[0])