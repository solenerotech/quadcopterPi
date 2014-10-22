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

# beta1:
#TARGET: 1)take off...
#2014.04.27

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
#

###############################################################################


from quadcopter import quadcopter
from logger_manager import setupLogger
#import curses
import argparse
from mode_PID import mode_PID
from mode_UAV import mode_UAV
from time import sleep

try:

    #manage params
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='debug', action='store_true', help='set debug leveland save in : myQ_log.txt ')
    parser.add_argument('-s', dest='savelog', action='store_true', help='save log: myQ.csv ')
    parser.add_argument('-c', dest='calibIMU', action='store_true', help='Calibrate IMU')
    parser.add_argument('-n', dest='netscan', action='store_true', help='Check network connection')
    args = parser.parse_args()

    #init logger
    logger = setupLogger('myQ', args.debug, 'myQ_log.txt')
    logger.info('myQ starting...Fasten your seat belt')


    #screen = curses.initscr()
    myQ = quadcopter('qpi', pin0=18, pin1=23, pin2=24, pin3=25, simulation=False)
    #GPIO: 18 23 24 25
    #pin : 12 16 18 22

    myQ.savelog = args.savelog
    myQ.calibIMU = args.calibIMU
    myQ.debuglev = args.debug
    myQ.netscanning = args.netscan  # TODO when fully tested , set  netscan on, by default

    myQ.load('myQ_cfg.txt')

    #Init sensor
    if myQ.calibIMU:
        myQ.sensor.calibrate()

    myQ.start()

    if myQ.netscanning is True:
        myQ.netscan.start()
    else:
        myQ.netscan.stop()
        myQ.netscan.connectionUp = True

    #Init PIDs
    #meglio per ora : 0,035 0 0      0,08 0,05 0
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
            pass
        elif myQ.rc.mode == myQ.rc.MODE_MOTOR:
            pass
        elif myQ.rc.mode == myQ.rc.MODE_PID_TUNING:
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

        sleep(0.1)

finally:
    # shut down cleanly
    myQ.stop()

logger.info('Thank you for joining us on this trip !')
logger.info('We are looking forward to seeing you on board again in the near future!')
logger.info('myQ stopped.')


