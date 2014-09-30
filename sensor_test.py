#solenero.tech@gmail.com
#solenerotech.wordpress.com

from sensor import sensor
import curses
from logger_manager import setupLogger


import argparse

logger = setupLogger('myQ', True, 'sensor_log.txt')

calibIMU = False
parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='calibIMU', action='store_true', help='Calibrate IMU')
args = parser.parse_args()
calibIMU = args.calibIMU

mySensor = sensor()

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

try:

    cycling = True
    while cycling:

        s = '|roll: ' + str(mySensor.roll)
        s += '|pitch: ' + str(mySensor.pitch)
        s += '|yaw: ' + str(mySensor.yaw)
        screen.clear()
        screen.addstr(1, 1, 'Press any button to stop')
        screen.addstr(2, 2, s)
        #timeout in millis
        screen.timeout(500)
        #getch returns -1 if timeout
        res = screen.getch()

        if res is not -1:
            cycling = False

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