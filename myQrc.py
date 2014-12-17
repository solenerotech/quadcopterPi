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


#2014.05.22 code is ready for test.
#at startup all motors starts at 5%
#to start pid control set the rc.command 1 (R),2(RP) or other to stop pid control'

#2014.08.02
#added  roll_rate  PID
#added initLog
#new log in csv format, easily to import in xcel
#2014.09.09
#added logger manager for all the classes
#added myQ.start()

#2014.10.1
#beta 3
#added netscan in quadcopter to verify the connection with remote control (device with fixed ip)


# myQ Release candidate
#2014.10.20
#create the modes (a collection of the previous functionalities present in the xyz_test.py
#create a module for each mode

#2014.11.04  added the webserver to remote control the myQ  using any devices (smarthphone, tablet)
#the current webpage it is really an example page with no all the functionalities

###############################################################################

#TODO Create a fling mode where the orientation is mantained and a mode where the orientation is manages
#as a pulse (get roll inclination than set it back to zero

#TODO consider to create a tack time  in myQ than can sync all the threads.Do first performance test...
#time() is time consuming. better to have only one call on it. still better could be to use a PWM output to trig the
#tack time

#TODO consider to add a button to save W-hover and a button to set Wh

from quadcopter import quadcopter
from loggingQ import setupLogger
import argparse
from mode_ESC import mode_ESC
from mode_PID import mode_PID
from mode_UAV import mode_UAV
from mode_Motor import mode_Motor
from time import sleep

try:

    myQ = None

    #manage params
    parser = argparse.ArgumentParser(
            description='MyQ- quadricopter controlled by raspberrypi', epilog="Are U ready to fly?")
    parser.add_argument('-d', dest='debug', action='store_true', help='save debug log: myQ.log ')
    parser.add_argument('-s', dest='savelog', action='store_true', help='save my Q data log: myQ.csv ')
    parser.add_argument('-i', dest='imulog', action='store_true', help='save IMU data log: myQ_sensor.csv')
    parser.add_argument('-ip', dest='ip', action='store', help='set ip addres for netscan')
    parser.add_argument('-c', dest='calibIMU', action='store_true', help='Calibrate IMU')
    parser.add_argument('-n', dest='netscan', action='store_true', help='Start network check')
    parser.add_argument('-w', dest='webserver', action='store_true', help='Start webserver|http//:192.68.0.10/myQ.html')
    args = parser.parse_args()

#TODO move this options in mode_init

    #init logger
    logger = setupLogger('myQ', args.debug, 'myQ.log')
    logger.info('myQ starting...')
    logger.info('Fasten your seat belt')

    #screen = curses.initscr()
    myQ = quadcopter('qpi', pin0=18, pin1=23, pin2=24, pin3=25, simulation=False)
    #GPIO: 18 23 24 25
    #pin : 12 16 18 22

    myQ.imulog = args.imulog
    myQ.savelog = args.savelog
    myQ.calibIMU = args.calibIMU
    myQ.debuglev = args.debug
    myQ.netscanOn = args.netscan  # TODO when fully tested , set  netscan on, by default
    myQ.webserverOn = args.webserver

    myQ.load('myQ.cfg')

    if args.ip is not None:
            logger.debug('New IP Address to scan: ' + args.ip)
            myQ.ip = args.ip
            myQ.save('myQ.cfg')

    #Init sensor
    if myQ.calibIMU:
        myQ.sensor.calibrate()

    myQ.start()

    if myQ.imulog is True:
        myQ.sensor.imulog = True
        logger.debug('IMU data: saving in myQ_sensor.csv')

    #set netscan ip according to myQ.cfg
    myQ.netscan.ip = myQ.ip
    if myQ.netscanOn is True:
        myQ.netscan.start()
    else:
        myQ.netscan.stop()
        sleep(0.1)
        myQ.netscan.connectionUp = True

    if myQ.webserverOn is True:
        myQ.webserver.start()

    myQ.display.refreshtime = 0.1

    #Init PIDs
    myQ.pidR.set(0.045, 0, 0, maxCorr=15)
    myQ.pidP.set(0.045, 0, 0, maxCorr=15)
    myQ.pidY.set(0, 0, 0)

    myQ.pidR_rate.set(0.070, 0.025, 0.010, maxCorr=15)
    myQ.pidP_rate.set(0.070, 0.025, 0.010, maxCorr=15)
    myQ.pidY_rate.set(0, 0, 0)

    while myQ.rc.cycling:
        if myQ.rc.mode == myQ.rc.MODE_INIT:
            pass
        elif myQ.rc.mode == myQ.rc.MODE_ESC:
            mode_ESC(myQ)
        elif myQ.rc.mode == myQ.rc.MODE_MOTOR:
            mode_Motor(myQ)
        elif myQ.rc.mode == myQ.rc.MODE_PID_TUNING:
            myQ.display.paused = True  # to minimize cpu load
            mode_PID(myQ)
        elif myQ.rc.mode == myQ.rc.MODE_FLYING:
            pass
        elif myQ.rc.mode == myQ.rc.MODE_UAV:
            mode_UAV(myQ)
        else:
            pass
        if myQ.rc.command == -1:
            #in idle mode, always stop motors
            myQ.motor[0].setW(0)
            myQ.motor[1].setW(0)
            myQ.motor[2].setW(0)
            myQ.motor[3].setW(0)
            myQ.display.paused = False

        sleep(0.1)

finally:
    # shut down cleanly
    if myQ is not None:
        myQ.stop()
        logger.info('Thank you for joining us on this trip!')
        logger.info('myQ stopped.')