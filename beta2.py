# -*- coding: utf-8 -*-
#solenero.tech@gmail.com
#solenerotech.wordpress.com
# beta1:
#TARGET: 1)take off...
#2014.04.27

#2014.05.22 code is ready for test.
#at startup all motors starts at 5%
#to start pid control set the rc.command 1 (R),2(RP) or other to stop pid control'

#TODO
#creando class display, con altro thread in parallelo...


#2014.08.02
#added  roll_rate  PID
#added initLog
#new log in csv format, esaly to import in xcl

def initLog():

    datalog = 'P ' + str(myQ.pidR.kp)
    datalog += ';I ' + str(myQ.pidR.ki)
    datalog += ';D ' + str(myQ.pidR.kd)
    datalog = ';rr P ' + str(myQ.pidR.kp)
    datalog += ';rr I ' + str(myQ.pidR.ki)
    datalog += ';rr D ' + str(myQ.pidR.kd)
    datalog += '\n'
    datalog += 'time;command;Rtarget;Roll;R rate;R rate gyro;throttle;rP;rI;rD;rrP;rrI;rrD;corr\n'

    return datalog


def addLog():
    #s1 =str(time())
    s1 = str(round(currentTime - initTime, 3))
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


def initDisplay():

    #Init display
    # turn off input echoing
    curses.noecho()
    # respond to keys immediately (don't wait for enter)
    curses.cbreak()
    # map arrow keys to special v1alues
    screen.keypad(True)


def showDisplay(displayCounter):

        screen.clear()
        i = 1
        screen.addstr(i, 0, '|-------------------------------------------------|')

        i = i + 1
        screen.addstr(i, 00, '|motor')
        screen.addstr(i, 10, '|')
        screen.addstr(i, 11, '|' + myQ.motor[0].name)
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, '|' + myQ.motor[1].name)
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, '|' + myQ.motor[2].name)
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, '|' + myQ.motor[3].name)
        screen.addstr(i, 50, '|')

        i = i + 1
        screen.addstr(i, 0, '|W')
        screen.addstr(i, 10, '|W')
        screen.addstr(i, 11, str(myQ.motor[0].getW()))
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, str(myQ.motor[1].getW()))
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, str(myQ.motor[2].getW()))
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, str(myQ.motor[3].getW()))
        screen.addstr(i, 50, '|')

        i = i + 1
        screen.addstr(i, 0, '|-------------------------------------------------|')
        i = i + 1
        screen.addstr(i, 00, '|')
        screen.addstr(i, 10, '|')
        screen.addstr(i, 11, 'Roll')
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, 'Pitch')
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, 'Yaw')
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, 'Throttle')
        screen.addstr(i, 50, '|')
        i = i + 1
        screen.addstr(i, 00, '|target')
        screen.addstr(i, 10, '|')
        screen.addstr(i, 11, '%.3f' % myQ.rc.roll)
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, '%.3f' % myQ.rc.pitch)
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, '%.3f' % myQ.rc.yaw)
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, '%.3f' % myQ.rc.throttle)
        screen.addstr(i, 50, '|')
        i = i + 1
        screen.addstr(i, 00, '|current')
        screen.addstr(i, 10, '|')
        screen.addstr(i, 11, '%.3f' % myQ.sensor.roll)
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, '%.3f' % myQ.sensor.pitch)
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, '%.3f' % myQ.sensor.yaw)
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, '%.3f' % myQ.rc.throttle)
        screen.addstr(i, 50, '|')
        i = i + 1
        screen.addstr(i, 0, '|-------------------------------------------------|')

        #if optione fai vedere...
        #displayPIDTuning()

#def displayPIDTuning():

        i = 10
        screen.addstr(i, 00, '|Command')
        screen.addstr(i, 10, '|')
        screen.addstr(i, 11, 'r kp')
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, '|rr kp')
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, 'rr ki')
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, 'rr kd')
        screen.addstr(i, 50, '|')
        i = i + 1
        screen.addstr(i, 00, '|%.3f' % myQ.rc.command)
        screen.addstr(i, 10, '|')
        screen.addstr(i, 11, '%.3f' % myQ.pidR.kp)
        screen.addstr(i, 20, '|')
        screen.addstr(i, 21, '%.3f' % myQ.pidR_rate.kp)
        screen.addstr(i, 30, '|')
        screen.addstr(i, 31, '%.3f' % myQ.pidR_rate.ki)
        screen.addstr(i, 40, '|')
        screen.addstr(i, 41, '%.3f' % myQ.pidR_rate.kd)
        screen.addstr(i, 50, '|')

        i = i + 1
        screen.addstr(i, 00, 'COMMAND > 0   NO PID control')
        i = i + 1
        screen.addstr(i, 00, 'COMMAND > 9   NO PID control - NO Motors')
        i = i + 1
        screen.addstr(i, 00, 'COMMAND > 1   PID control  roll')
        i = i + 1
        screen.addstr(i, 00, 'COMMAND >  2<R  RR: 3<P>4   5<I>6   7<D>8')
        i = i + 1
        screen.addstr(i, 00, 'z < ROLL > a     n < PITCH > m     f < THROTLE > t')
        i = i + 1
        screen.addstr(i, 00, 'SPACEBAR to KILL')


###############################################################################

from quadcopter import quadcopter

import curses
import argparse
from time import time, sleep, strftime


cycleTime = 0.010  # [s]
currentDate = strftime("%Y.%m.%d_%H.%M.%S")
datalog = ''
#update display every displaytime [s]

displayCounter = 0

#manage params
parser = argparse.ArgumentParser()
parser.add_argument('-s', dest='savelog', action='store_true', help='save log: myQ_date.txt ')
parser.add_argument('-c', dest='calibIMU', action='store_true', help='Calibrate IMU')
args = parser.parse_args()
savelog = args.savelog
calibIMU = args.calibIMU


#logger = setupLogger('qpi')
screen = curses.initscr()
myQ = quadcopter('qpi', screen, pin0=18, pin1=23, pin2=24, pin3=25, simulation=False)
#GPIO: 18 23 24 25
#pin : 12 16 18 22


#Init sensor
if calibIMU:
    print 'Sensor calibrating...'
    myQ.sensor.calibrate()
print 'Sensor starting...'

myQ.sensor.start()

#Init remote control
print 'Remote Control starting...'
myQ.rc.start()

#Init PIDs
print 'PID initializing...'
#meglio per ora : 0,035 0 0      0,08 0,05 0
myQ.pidR.set(0.045, 0, 0, maxCorr=15)
myQ.pidP.set(0.045, 0, 0, maxCorr=15)
myQ.pidY.set(0, 0, 0)

myQ.pidR_rate.set(0.070, 0.025, 0.010, maxCorr=15)
myQ.pidP_rate.set(0.070, 0.025, 0.010, maxCorr=15)
myQ.pidY_rate.set(0, 0, 0)

#InitDisplay
print 'Display starting...'
initDisplay()

#init Log
datalog = initLog()

#------------Start Moving---------
#Init motors
for i in xrange(4):
    print 'Motor ' + str(i) + ' starting...'
    myQ.motor[i].start()
    myQ.motor[i].setW(0)
    #sleep(5) #used to ear clearly all motor status

#Start Motors
myQ.rc.throttle = 5
myQ.motor[0].setW(myQ.rc.throttle)
#myQ.motor[1].setW(myQ.rc.throttle)
myQ.motor[2].setW(myQ.rc.throttle)
#myQ.motor[3].setW(myQ.rc.throttle)

#TODO Metti tutto quello che c'e di sopra  in un  modulo nuovo  qpi che
#gestisce le varie opzioni , equello che c'e di sotto in un modulo beta3.py'

#-----------Main Loop-------------
initTime = time()
previousTime = initTime
currentTime = initTime
displayCounter = 0

corrR = 0
corrP = 0
corrY = 0
roll_rate_target = 0
pitch_rate_target = 0


try:

    while myQ.rc.cycling:

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
            currP = myQ.pidR.kp + 0.001
            currI = myQ.pidR.ki
            currD = myQ.pidR.kd
            myQ.pidR.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 3:
            currP = myQ.pidR_rate.kp + 0.001
            currI = myQ.pidR_rate.ki
            currD = myQ.pidR_rate.kd
            myQ.pidR_rate.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 4:
            currP = myQ.pidR_rate.kp - 0.001
            currI = myQ.pidR_rate.ki
            currD = myQ.pidR_rate.kd
            myQ.pidR_rate.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 5:
            currP = myQ.pidR_rate.kp
            currI = myQ.pidR_rate.ki + 0.001
            currD = myQ.pidR_rate.kd
            myQ.pidR_rate.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 6:
            currP = myQ.pidR_rate.kp
            currI = myQ.pidR_rate.ki - 0.001
            currD = myQ.pidR_rate.kd
            myQ.pidR_rate.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 7:
            currP = myQ.pidR_rate.kp
            currI = myQ.pidR_rate.ki
            currD = myQ.pidR_rate.kd + 0.001
            myQ.pidR_rate.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 8:
            currP = myQ.pidR_rate.kp
            currI = myQ.pidR_rate.ki
            currD = myQ.pidR_rate.kd - 0.001
            myQ.pidR_rate.set(currP, currI, currD, maxCorr=15)
            myQ.rc.command = 1
        elif  myQ.rc.command == 9:
            myQ.rc.throttle = 0
            corrR = 0
            corrP = 0
        else:
            corrR = 0
            corrP = 0

        #TODO add yaw pid control here and throttle pid control

        #The sign used to add the correction depends on the
        # motor position respect the IMU orientation
        myQ.motor[0].setW(myQ.rc.throttle + corrR)
        myQ.motor[2].setW(myQ.rc.throttle - corrR)


        #myQ.motor[1].setW(myQ.rc.throttle - corrP)
        #myQ.motor[3].setW(myQ.rc.throttle + corrP)


        displayTime = 0.2
        displayCounter += 1
        if displayCounter > displayTime / cycleTime:
            displayCounter = 0
        if displayCounter == 0:
            showDisplay(displayCounter)

        if savelog is True:
            datalog += addLog()

finally:
    # shut down cleanly
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
    #
    myQ.stop()

    if savelog:
        #with open(currentDate + ' myQ.txt', 'w+') as data_file:
        with open('myQ.csv', 'w+') as data_file:
            data_file.write(datalog)
            data_file.flush()


