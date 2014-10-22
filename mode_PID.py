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


def mode_PID(myQ):

    logger = logging.getLogger('myQ.mode_UAV')

    cycleTime = 0.010  # [s]

    #init Log
    datalog = ''
    datalog = initLog(myQ)

    corrR = 0
    corrP = 0
    corrY = 0
    roll_rate_target = 0
    pitch_rate_target = 0

    myQ.rc.throttle = 0

    tuningRollRate = True


    try:

        #wait ack from user to start motors
        while myQ.rc.command != 9 and myQ.rc.command !=-1 and myQ.rc.cycling:
            pass

        if myQ.rc.command !=-1:
            myQ.rc.command = 0

        initTime = time()
        previousTime = initTime
        currentTime = initTime

        #displayCommand()
        while myQ.rc.cycling is True and  myQ.rc.command !=-1:

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

                #TODO remove to activate pitch
                #corrP = 0

            elif myQ.rc.command == 2:
                #swtch between roll and roll rate tuning
                if tuningRollRate is True:
                    tuningRollRate = False
                else:
                    tuningRollRate = True
                myQ.rc.command = 1

            elif  myQ.rc.command == 3:
                if tuningRollRate is True:
                    myQ.pidR_rate.set(myQ.pidR_rate.kp + 0.001, myQ.pidR_rate.ki, myQ.pidR_rate.kd, maxCorr=15)
                else:
                    myQ.pidR.set(myQ.pidR.kp + 0.001, myQ.pidR.ki, myQ.pidR.kd, maxCorr=15)
                myQ.rc.command = 1

            elif  myQ.rc.command == 4:
                if tuningRollRate is True:
                    myQ.pidR_rate.set(myQ.pidR_rate.kp - 0.001, myQ.pidR_rate.ki, myQ.pidR_rate.kd, maxCorr=15)
                else:
                    myQ.pidR.set(myQ.pidR.kp - 0.001, myQ.pidR.ki, myQ.pidR.kd, maxCorr=15)
                myQ.rc.command = 1

            elif  myQ.rc.command == 5:
                if tuningRollRate is True:
                    myQ.pidR_rate.set(myQ.pidR_rate.kp  , myQ.pidR_rate.ki+ 0.001, myQ.pidR_rate.kd, maxCorr=15)
                else:
                    myQ.pidR.set(myQ.pidR.kp , myQ.pidR.ki+ 0.001, myQ.pidR.kd, maxCorr=15)
                myQ.rc.command = 1

            elif  myQ.rc.command == 6:
                if tuningRollRate is True:
                    myQ.pidR_rate.set(myQ.pidR_rate.kp , myQ.pidR_rate.ki - 0.001, myQ.pidR_rate.kd, maxCorr=15)
                else:
                    myQ.pidR.set(myQ.pidR.kp  , myQ.pidR.ki - 0.001, myQ.pidR.kd, maxCorr=15)
                myQ.rc.command = 1

            elif  myQ.rc.command == 7:
                if tuningRollRate is True:
                    myQ.pidR_rate.set(myQ.pidR_rate.kp  , myQ.pidR_rate.ki, myQ.pidR_rate.kd + 0.001, maxCorr=15)
                else:
                    myQ.pidR.set(myQ.pidR.kp, myQ.pidR.ki, myQ.pidR.kd + 0.001, maxCorr=15)
                myQ.rc.command = 1

            elif  myQ.rc.command == 8:
                if tuningRollRate is True:
                    myQ.pidR_rate.set(myQ.pidR_rate.kp, myQ.pidR_rate.ki, myQ.pidR_rate.kd - 0.001, maxCorr=15)
                else:
                    myQ.pidR.set(myQ.pidR.kp , myQ.pidR.ki, myQ.pidR.kd - 0.001, maxCorr=15)
                myQ.rc.command = 1


            #TODO add yaw pid control here and throttle pid control

            #The sign used to add the correction depends on the
            # motor position respect the IMU orientation
            myQ.motor[0].setW(myQ.rc.throttle + corrR)
            myQ.motor[2].setW(myQ.rc.throttle - corrR)

            #myQ.motor[1].setW(myQ.rc.throttle - corrP)
            #myQ.motor[3].setW(myQ.rc.throttle + corrP)

            if myQ.savelog is True:
                datalog += addLog(myQ, currentTime - initTime)

    finally:
        try:
            if myQ.savelog:
                with open('myQ.csv', 'w+') as data_file:
                    data_file.write(datalog)
                    data_file.flush()
        except IOError, err:
            logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'myQ.csv')



def initLog(myQ):

    datalog = 'P ' + str(myQ.pidR.kp)
    datalog += ';I ' + str(myQ.pidR.ki)
    datalog += ';D ' + str(myQ.pidR.kd)
    datalog = ';rr P ' + str(myQ.pidR.kp)
    datalog += ';rr I ' + str(myQ.pidR.ki)
    datalog += ';rr D ' + str(myQ.pidR.kd)
    datalog += '\n'
    datalog += 'time;command;Rtarget;Roll;R rate;R rate gyro;throttle;rP;rI;rD;rrP;rrI;rrD;corr\n'

    return datalog


def addLog(self, myQ, deltatime):
    #s1 =str(time())
    s1 = str(round(deltatime, 3))
    s1 += ';' + str(myQ.rc.command)
    s1 += ';' + str(myQ.rc.roll)
    s1 += ';' + str(myQ.sensor.roll)
    s1 += ';' + str(myQ.sensor.roll_rate)
    s1 += ';' + str(myQ.sensor.r_rate)
    #s1 += ';'+ str(myQ.rc.pitch)
    #s1 += ';'+str(myQ.sensor.pitch)
    #s1 += ';'+ str(myQ.rc.yaw)
    #s1 += ';'+str(myQ.sensor.yaw)
    s1 += ';' + str(myQ.rc.throttle)
    #s1 += ';'+str(myQ.motor[0].getW())
    #s1 += ';'+str(myQ.motor[1].getW())
    #s1 += ';'+str(myQ.motor[2].getW())
    #s1 += ';'+str(myQ.motor[3].getW())
    s1 += ';' + str(myQ.pidR.P)
    s1 += ';' + str(myQ.pidR.I)
    s1 += ';' + str(myQ.pidR.D)
    s1 += ';' + str(myQ.pidR_rate.P)
    s1 += ';' + str(myQ.pidR_rate.I)
    s1 += ';' + str(myQ.pidR_rate.D)
    s1 += ';' + str(myQ.pidR_rate.corr)
    s1 += '\n'
    return s1