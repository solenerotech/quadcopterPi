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

#2014.10.20   finalize display
#removed all the reference to screen  in th erest of the code

import curses
import threading
from time import sleep
import logging


class display(threading.Thread):

#here i can manage the display as a parallel thread
    def __init__(self, quadricopter, refreshtime=0.2):

        threading.Thread.__init__(self)
        self.logger = logging.getLogger('myQ.display')
        self.myQ = quadricopter
        self.cycling = True
        self.screen = curses.initscr()
        self.refreshtime = refreshtime

    def displayQ(self):

        i = 0
        self.screen.addstr(i, 0, '|-------------------------------------------------|')
        i = 1
        self.screen.addstr(i, 00, '|motor')
        self.screen.addstr(i, 10, '|')
        self.screen.addstr(i, 11, self.myQ.motor[0].name)
        self.screen.addstr(i, 20, '|')
        self.screen.addstr(i, 21, self.myQ.motor[1].name)
        self.screen.addstr(i, 30, '|')
        self.screen.addstr(i, 31, self.myQ.motor[2].name)
        self.screen.addstr(i, 40, '|')
        self.screen.addstr(i, 41, self.myQ.motor[3].name)
        self.screen.addstr(i, 50, '|')
        i = 2
        self.screen.addstr(i, 0, '|W')
        self.screen.addstr(i, 10, '|W')
        self.screen.addstr(i, 11, str(self.myQ.motor[0].getW()))
        self.screen.addstr(i, 20, '|')
        self.screen.addstr(i, 21, str(self.myQ.motor[1].getW()))
        self.screen.addstr(i, 30, '|')
        self.screen.addstr(i, 31, str(self.myQ.motor[2].getW()))
        self.screen.addstr(i, 40, '|')
        self.screen.addstr(i, 41, str(self.myQ.motor[3].getW()))
        self.screen.addstr(i, 50, '|')

        i = 3
        self.screen.addstr(i, 0, '|-------------------------------------------------|')
        i = 4
        self.screen.addstr(i, 00, '|')
        self.screen.addstr(i, 10, '|')
        self.screen.addstr(i, 11, 'Roll')
        self.screen.addstr(i, 20, '|')
        self.screen.addstr(i, 21, 'Pitch')
        self.screen.addstr(i, 30, '|')
        self.screen.addstr(i, 31, 'Yaw')
        self.screen.addstr(i, 40, '|')
        self.screen.addstr(i, 41, 'Throttle')
        self.screen.addstr(i, 50, '|')
        i = 5
        self.screen.addstr(i, 00, '|target')
        self.screen.addstr(i, 10, '|')
        self.screen.addstr(i, 11, '%.3f' % self.myQ.rc.roll)
        self.screen.addstr(i, 20, '|')
        self.screen.addstr(i, 21, '%.3f' % self.myQ.rc.pitch)
        self.screen.addstr(i, 30, '|')
        self.screen.addstr(i, 31, '%.3f' % self.myQ.rc.yaw)
        self.screen.addstr(i, 40, '|')
        self.screen.addstr(i, 41, '%.3f' % self.myQ.rc.throttle)
        self.screen.addstr(i, 50, '|')
        i = 6
        self.screen.addstr(i, 00, '|current')
        self.screen.addstr(i, 10, '|')
        self.screen.addstr(i, 11, '%.3f' % self.myQ.sensor.roll)
        self.screen.addstr(i, 20, '|')
        self.screen.addstr(i, 21, '%.3f' % self.myQ.sensor.pitch)
        self.screen.addstr(i, 30, '|')
        self.screen.addstr(i, 31, '%.3f' % self.myQ.sensor.yaw)
        self.screen.addstr(i, 40, '|')
        self.screen.addstr(i, 41, '%.3f' % self.myQ.rc.throttle)
        self.screen.addstr(i, 50, '|')
        i = 7
        self.screen.addstr(i, 0, '|-------------------------------------------------|')

        i = 0
        self.screen.addstr(i, 51, '----------------------------|')
        i = 1
        self.screen.addstr(i, 51, 'Mode: %d' % self.myQ.rc.mode)
        self.screen.addstr(i, 79, '|')
        i = 2
        self.screen.addstr(i, 51, 'Command: %d' % self.myQ.rc.command)
        self.screen.addstr(i, 79, '|')
        i = 3
        self.screen.addstr(i, 51, '----------------------------|')
        i = 4
        self.screen.addstr(i, 51, '       |   P  |   I  |   D  |')
        i = 5
        self.screen.addstr(i, 51, 'roll')
        self.screen.addstr(i, 58, '|%.3f ' % self.myQ.pidR.kp)
        self.screen.addstr(i, 65, '|%.3f ' % self.myQ.pidR.ki)
        self.screen.addstr(i, 72, '|%.3f |' % self.myQ.pidR.kd)
        i = 6
        self.screen.addstr(i, 51, 'r rate')
        self.screen.addstr(i, 58, '|%.3f ' % self.myQ.pidR_rate.kp)
        self.screen.addstr(i, 65, '|%.3f ' % self.myQ.pidR_rate.ki)
        self.screen.addstr(i, 72, '|%.3f |' % self.myQ.pidR_rate.kd)
        i = 7
        self.screen.addstr(i, 51, '')
        self.screen.addstr(i, 79, '|')
        i = 7
        self.screen.addstr(i, 51, '----------------------------|')
        i = 8
        self.screen.addstr(i, 0, '|SPACEBAR to KILL')
        self.screen.addstr(i, 20, '|    z < Roll > a    ')
        self.screen.addstr(i, 40, '|    m < Pitch > n')
        self.screen.addstr(i, 60, '| f < Throttle > t')
        self.screen.addstr(i, 79, '|')

    def displayMode_init(self):
        i = 14
        self.screen.addstr(i, 00, 'welcome')
        i = i + 1
        self.screen.addstr(i, 00, 'here add option to be managed')

    def displayMode_esc(self):
        i = 14
        self.screen.addstr(i, 00, 'esc initialization')
        i = i + 1
        self.screen.addstr(i, 00, 'here add description of procedure and commands')

    def displayMode_motor(self):
        i = 14
        self.screen.addstr(i, 00, 'motor testing')
        i = i + 1
        self.screen.addstr(i, 00, 'here add description of procedure and commands')

    def displayMode_pid(self):
        i = 14
        self.screen.addstr(i, 00, 'FIRST : Press 9  to ack the motor start')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 0   NO PID control')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 1   PID control  roll')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 2   Switch tune RollRate/Roll')
        i = i + 1
        self.screen.addstr(i, 00, 'Tune Roll Rate/roll PID:')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 3<P>4   5<I>6   7<D>8')

    def displayMode_flying(self):
        i = 14
        self.screen.addstr(i, 00, 'flying mode ')
        i = i + 1
        self.screen.addstr(i, 00, 'here add description of procedure and commands')

    def displayMode_uav(self):
        i = 14
        self.screen.addstr(i, 00, 'FIRST : Press 9  to ack the motor start')
        i = i + 1
        self.screen.addstr(i, 00, 'uav mode')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 0   NO PID control')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 1   PID control  roll')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 2   3 sec pulse roll 0|3  for 18 sec')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 3   3 sec pulse roll -3|3  for 18 sec')
        i = i + 1
        self.screen.addstr(i, 00, 'COMMAND > 4   variations  for 20 sec')

    def displayModeQ(self):
        i = 11

        self.screen.addstr(i, 00, '|___INIT__')
        self.screen.addstr(i, 10, '|___ESC___')
        self.screen.addstr(i, 20, '|___Motor_')
        self.screen.addstr(i, 30, '|___PID___')
        self.screen.addstr(i, 40, '|__Flying_')
        self.screen.addstr(i, 50, '|___UAV___')
        self.screen.addstr(i, 60, '|___void__')
        self.screen.addstr(i, 70, '|___void__')
        self.screen.addstr(i, 79, '|')

        i = 11
        if self.myQ.rc.mode == self.myQ.rc.MODE_INIT:
            self.screen.addstr(i, 00, '|___INIT__', curses.A_REVERSE)
            self.displayMode_init()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_ESC:
            self.screen.addstr(i, 10, '|___ESC___', curses.A_REVERSE)
            self.displayMode_esc()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_MOTOR:
            self.screen.addstr(i, 20, '|___Motor_', curses.A_REVERSE)
            self.displayMode_motor()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_PID_TUNING:
            self.screen.addstr(i, 30, '|___PID___', curses.A_REVERSE)
            self.displayMode_pid()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_FLYING:
            self.screen.addstr(i, 40, '|__Flying_', curses.A_REVERSE)
            self.displayMode_flying()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_UAV:
            self.screen.addstr(i, 50, '|___UAV___', curses.A_REVERSE)
            self.displayMode_uav()
        elif self.myQ.rc.mode == 6:
            self.screen.addstr(i, 60, '|___void__', curses.A_REVERSE)
        elif self.myQ.rc.mode == 7:
            self.screen.addstr(i, 70, '|___void__', curses.A_REVERSE)
        self.screen.addstr(i, 79, '|')

        i = 20
        self.screen.addstr(i, 00, '')  # used to set the cursor in a fixed position

    def run(self):
        self.logger.debug('DISPLAY running...')

        # turn off input echoing
        curses.noecho()
        # respond to keys immediately (don't wait for enter)
        curses.cbreak()
        curses.curs_set(0)
        # map arrow keys to special v1alues
        self.screen.keypad(True)
        self.screen.clear()
        while self.cycling is True:
            self.screen.clear()
            self.displayQ()
            self.displayModeQ()
            self.screen.refresh()
            sleep(self.refreshtime)

    def stop(self):

        self.logger.debug('DISPLAY stopping...')

        self.cycling = False
        sleep(self.refreshtime+0.1)
        self.screen.clear()
        self.screen.addstr(0, 0, '')
        self.screen.keypad(0)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()