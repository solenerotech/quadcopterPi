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

from sensor import sensor
import curses
from loggingQ import setupLogger


import argparse

logger = setupLogger('myQ', True, 'sensor_test.log')

calibIMU = False
parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='calibIMU', action='store_true', help='Calibrate IMU')
parser.add_argument('-i', dest='imulog', action='store_true', help='save IMU data log: myQ_sensor.csv')
args = parser.parse_args()
calibIMU = args.calibIMU
imuLog = args.imulog

mySensor = sensor(imulog=imuLog, simulation=False)

if calibIMU:
    mySensor.calibrate()

mySensor.start()


screen = curses.initscr()
# turn off input echoing
curses.noecho()
# respond to keys immediately (don't wait for enter)
curses.cbreak()
# map arrow keys to special values
screen.keypad(True)
#timeout in millis
screen.timeout(500)


try:

    cycling = True
    #cycling = False
    while cycling:

        s = ' IMU |roll: ' + str(mySensor.roll)
        s += '|pitch: ' + str(mySensor.pitch)
        s += '|yaw: ' + str(mySensor.yaw)

        s1 = 'ACCEL|roll: ' + str(mySensor.roll_a)
        s1 += '|pitch: ' + str(mySensor.pitch_a)
        s1 += '|yaw: ' + str(mySensor.yaw_a)

        s2 = 'GYRO |roll: ' + str(mySensor.roll_g)
        s2 += '|pitch: ' + str(mySensor.pitch_g)
        s2 += '|yaw: ' + str(mySensor.yaw_g)

        #screen.clear()
        screen.addstr(1, 1, 'Press any button to stop')
        screen.addstr(3, 1, s)
        screen.addstr(5, 1, s1)
        screen.addstr(7, 1, s2)
        #getch returns -1 if timeout
        res = screen.getch()

        if res is not -1:
            cycling = False

    #sleep(10)

finally:
    # shut down cleanly
    #
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    #here the sensor stops to collect data
    mySensor.stop()
    curses.endwin()

    logger.debug("well done!")
