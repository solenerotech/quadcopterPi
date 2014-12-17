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
#removed all the reference to screen  in the rest of the code

import curses
import threading
from time import sleep, time
import logging


class display(threading.Thread):

#here i can manage the display as a parallel thread
    def __init__(self, quadricopter, refreshtime=0.2):

        threading.Thread.__init__(self)
        self.logger = logging.getLogger('myQ.display')
        self.myQ = quadricopter
        self.cycling = True
        self.screen = curses.initscr()
        self.logQ = curses.newpad(3, 81)
        self.padQ = curses.newpad(11, 81)
        self.padModeQ = curses.newpad(11, 81)
        self.refreshtime = refreshtime
        self.paused = False
        self.currentMode = -1
        self.firstcycle = True

    def displayPadQ(self):

        #self.padQ.clear()
        self.padQ.redrawwin()
        i = 0
        self.padQ.addstr(i, 0, '|-------------------------------------------------|')
        i = 1
        self.padQ.addstr(i, 00, '|motor')
        self.padQ.addstr(i, 10, '|')
        self.padQ.addstr(i, 11, self.myQ.motor[0].name)
        self.padQ.addstr(i, 20, '|')
        self.padQ.addstr(i, 21, self.myQ.motor[1].name)
        self.padQ.addstr(i, 30, '|')
        self.padQ.addstr(i, 31, self.myQ.motor[2].name)
        self.padQ.addstr(i, 40, '|')
        self.padQ.addstr(i, 41, self.myQ.motor[3].name)
        self.padQ.addstr(i, 50, '|')
        i = 2
        self.padQ.addstr(i, 0, '|W')
        self.padQ.addstr(i, 10, '|W')
        self.padQ.addstr(i, 11, str(self.myQ.motor[0].getW()))
        self.padQ.addstr(i, 20, '|')
        self.padQ.addstr(i, 21, str(self.myQ.motor[1].getW()))
        self.padQ.addstr(i, 30, '|')
        self.padQ.addstr(i, 31, str(self.myQ.motor[2].getW()))
        self.padQ.addstr(i, 40, '|')
        self.padQ.addstr(i, 41, str(self.myQ.motor[3].getW()))
        self.padQ.addstr(i, 50, '|')
        i = 3
        self.padQ.addstr(i, 0, '|-------------------------------------------------|')
        i = 4
        self.padQ.addstr(i, 00, '|')
        self.padQ.addstr(i, 10, '|')
        self.padQ.addstr(i, 11, 'Roll')
        self.padQ.addstr(i, 20, '|')
        self.padQ.addstr(i, 21, 'Pitch')
        self.padQ.addstr(i, 30, '|')
        self.padQ.addstr(i, 31, 'Yaw')
        self.padQ.addstr(i, 40, '|')
        self.padQ.addstr(i, 41, 'Throttle')
        self.padQ.addstr(i, 50, '|')
        i = 5
        self.padQ.addstr(i, 00, '|target')
        self.padQ.addstr(i, 10, '|')
        self.padQ.addstr(i, 11, '%.3f' % self.myQ.rc.roll)
        self.padQ.addstr(i, 20, '|')
        self.padQ.addstr(i, 21, '%.3f' % self.myQ.rc.pitch)
        self.padQ.addstr(i, 30, '|')
        self.padQ.addstr(i, 31, '%.3f' % self.myQ.rc.yaw)
        self.padQ.addstr(i, 40, '|')
        self.padQ.addstr(i, 41, '%.3f' % self.myQ.rc.throttle)
        self.padQ.addstr(i, 50, '|')
        i = 6
        self.padQ.addstr(i, 00, '|current')
        self.padQ.addstr(i, 10, '|')
        self.padQ.addstr(i, 11, '%.3f' % self.myQ.sensor.roll)
        self.padQ.addstr(i, 20, '|')
        self.padQ.addstr(i, 21, '%.3f' % self.myQ.sensor.pitch)
        self.padQ.addstr(i, 30, '|')
        self.padQ.addstr(i, 31, '%.3f' % self.myQ.sensor.yaw)
        self.padQ.addstr(i, 40, '|')
        self.padQ.addstr(i, 41, '%.3f' % self.myQ.rc.throttle)
        self.padQ.addstr(i, 50, '|')
        i = 7
        self.padQ.addstr(i, 0, '|-------------------------------------------------|')

        i = 0
        self.padQ.addstr(i, 51, '----------------------------|')
        i = 1
        self.padQ.addstr(i, 51, 'Mode: %d' % self.myQ.rc.mode)
        self.padQ.addstr(i, 65, '|Temp: %.1f' % self.myQ.sensor.temp)
        self.padQ.addstr(i, 79, '|')
        i = 2
        self.padQ.addstr(i, 51, 'Command: %d' % self.myQ.rc.command)
        self.padQ.addstr(i, 65, '|')
        self.padQ.addstr(i, 79, '|')
        i = 3
        self.padQ.addstr(i, 51, '----------------------------|')
        i = 4
        self.padQ.addstr(i, 51, '       |   P  |   I  |   D  |')
        i = 5
        self.padQ.addstr(i, 51, 'roll')
        self.padQ.addstr(i, 58, '|%.3f ' % self.myQ.pidR.kp)
        self.padQ.addstr(i, 65, '|%.3f ' % self.myQ.pidR.ki)
        self.padQ.addstr(i, 72, '|%.3f |' % self.myQ.pidR.kd)
        i = 6
        self.padQ.addstr(i, 51, 'r rate')
        self.padQ.addstr(i, 58, '|%.3f ' % self.myQ.pidR_rate.kp)
        self.padQ.addstr(i, 65, '|%.3f ' % self.myQ.pidR_rate.ki)
        self.padQ.addstr(i, 72, '|%.3f |' % self.myQ.pidR_rate.kd)
        i = 7
        self.padQ.addstr(i, 51, '')
        self.padQ.addstr(i, 79, '|')
        i = 7
        self.padQ.addstr(i, 51, '----------------------------|')
        i = 8
        self.padQ.addstr(i, 00, '|    j < Roll > k    ')
        self.padQ.addstr(i, 20, '|    i < Pitch > m    ')
        self.padQ.addstr(i, 40, '|    a < yaw > s')
        self.padQ.addstr(i, 60, '| w < Throttle > z')
        self.padQ.addstr(i, 79, '|')
        i = 9
        self.padQ.addstr(i, 0, '|------------------------------|SPACEBAR to KILL|------------------------------|')
        self.padQ.refresh(0, 0, 0, 0, 9, 79)

    def displayMode_init(self):

        i = 1
        self.padModeQ.addstr(i, 00, 'Welcome to myQPI')
        self.padModeQ.clrtoeol()
        i = 2
        self.padModeQ.addstr(i, 00, 'use arrows to navigate along the modes.')
        self.padModeQ.clrtoeol()
        i = 3
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 4
        self.padModeQ.addstr(i, 00, 'Enjoy it , but first remember:')
        self.padModeQ.clrtoeol()
        i = 5
        self.padModeQ.addstr(i, 00, '                              !!!SAFETY!!!')
        self.padModeQ.clrtoeol()
        i = 6
        self.padModeQ.addstr(i, 00, 'before start any activity verify to be in a safe condition')
        self.padModeQ.clrtoeol()
        i = 7
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 8
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 9
        self.padModeQ.addstr(i, 0, '|------------------------------------------------------------------------------|')

    def displayMode_esc(self):

        i = 1
        self.padModeQ.addstr(i, 00, 'Follow the next steps to initialize ESCs')
        self.padModeQ.clrtoeol()
        i = 2
        self.padModeQ.addstr(i, 00, '1)FIX the Motor steady,remove the Props,connect the motor to ESC')
        self.padModeQ.clrtoeol()
        i = 3
        self.padModeQ.addstr(i, 00, '2)Disconnect the ESC power cables')
        self.padModeQ.clrtoeol()
        i = 4
        self.padModeQ.addstr(i, 00, '3)PRESS 9 to ack the motor start')
        self.padModeQ.clrtoeol()
        i = 5
        self.padModeQ.addstr(i, 00, '4)Select the ESC pressing 0|3')
        self.padModeQ.clrtoeol()
        i = 6
        self.padModeQ.addstr(i, 00, '5)Press 5 to ack to init ESC - ATT: throttle will be set to max')
        self.padModeQ.clrtoeol()
        i = 7
        self.padModeQ.addstr(i, 00, '6)Now Connect ESC power and wait beep-beep')
        self.padModeQ.clrtoeol()
        i = 8
        self.padModeQ.addstr(i, 00, '7)Press 6 to complete procedure (throttle to 0')
        self.padModeQ.clrtoeol()
        i = 9
        self.padModeQ.addstr(i, 0, '|------------------------------------------------------------------------------|')

    def displayMode_motor(self):
        i = 1
        self.padModeQ.addstr(i, 00, 'FIRST : Press 9  to ack the motor start')
        self.padModeQ.clrtoeol()
        i = 2
        self.padModeQ.addstr(i, 00, 'COMMAND > 0   Select M0 (default)')
        self.padModeQ.clrtoeol()
        i = 3
        self.padModeQ.addstr(i, 00, 'COMMAND > 1   Select M1')
        self.padModeQ.clrtoeol()
        i = 4
        self.padModeQ.addstr(i, 00, 'COMMAND > 2   Select M2')
        self.padModeQ.clrtoeol()
        i = 5
        self.padModeQ.addstr(i, 00, 'COMMAND > 3   Select M3')
        self.padModeQ.clrtoeol()
        i = 6
        self.padModeQ.addstr(i, 00, 'Use Throttle to modify motor speed')
        self.padModeQ.clrtoeol()
        i = 7
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 8
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 9
        self.padModeQ.addstr(i, 0, '|------------------------------------------------------------------------------|')

    def displayMode_pid(self):
        i = 1
        self.padModeQ.addstr(i, 00, 'FIRST : Press 9  to ack the motor start')
        self.padModeQ.clrtoeol()
        i = 2
        self.padModeQ.addstr(i, 00, 'COMMAND > 0   NO PID control')
        self.padModeQ.clrtoeol()
        i = 3
        self.padModeQ.addstr(i, 00, 'COMMAND > 1   PID control  roll')
        self.padModeQ.clrtoeol()
        i = 4
        self.padModeQ.addstr(i, 00, 'COMMAND > 2   Switch tune RollRate/Roll')
        self.padModeQ.clrtoeol()
        i = 5
        self.padModeQ.addstr(i, 00, 'Tune Roll Rate/roll PID:')
        self.padModeQ.clrtoeol()
        i = 6
        self.padModeQ.addstr(i, 00, 'COMMAND > 3<P>4   5<I>6   7<D>8')
        self.padModeQ.clrtoeol()
        i = 7
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 8
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 9
        self.padModeQ.addstr(i, 0, '|------------------------------------------------------------------------------|')

    def displayMode_flying(self):
        i = 1
        self.padModeQ.addstr(i, 00, 'FIRST : Press 9  to ack the motor start')
        self.padModeQ.clrtoeol()
        i = 2
        self.padModeQ.addstr(i, 00, 'COMMAND > 0   Netscan activation (to check continously the connection)')
        self.padModeQ.clrtoeol()
        i = 3
        self.padModeQ.addstr(i, 00, 'COMMAND > 1   Use PID value set 1')
        self.padModeQ.clrtoeol()
        i = 4
        self.padModeQ.addstr(i, 00, 'COMMAND > 2   Use PID value set 2')
        self.padModeQ.clrtoeol()
        i = 5
        self.padModeQ.addstr(i, 00, 'COMMAND > 3   Use PID value set 3')
        self.padModeQ.clrtoeol()
        i = 6
        self.padModeQ.addstr(i, 00, 'COMMAND > 4   Activate PID Control')
        self.padModeQ.clrtoeol()
        i = 7
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 8
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 9
        self.padModeQ.addstr(i, 0, '|------------------------------------------------------------------------------|')

    def displayMode_uav(self):
        i = 1
        self.padModeQ.addstr(i, 00, 'FIRST : Press 9  to ack the motor start')
        self.padModeQ.clrtoeol()
        i = 2
        self.padModeQ.addstr(i, 00, 'COMMAND > 0   NO PID control')
        self.padModeQ.clrtoeol()
        i = 3
        self.padModeQ.addstr(i, 00, 'COMMAND > 1   PID control  roll')
        self.padModeQ.clrtoeol()
        i = 4
        self.padModeQ.addstr(i, 00, 'COMMAND > 2   3 sec pulse roll 0|3  for 18 sec')
        self.padModeQ.clrtoeol()
        i = 5
        self.padModeQ.addstr(i, 00, 'COMMAND > 3   3 sec pulse roll -3|3  for 18 sec')
        self.padModeQ.clrtoeol()
        i = 6
        self.padModeQ.addstr(i, 00, 'COMMAND > 4   variations  for 20 sec')
        self.padModeQ.clrtoeol()
        i = 7
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 8
        self.padModeQ.addstr(i, 00, '')
        self.padModeQ.clrtoeol()
        i = 9
        self.padModeQ.addstr(i, 0, '|------------------------------------------------------------------------------|')

    def displayModeQ(self):

        self.padModeQ.redrawwin()

        #if self.currentMode == self.myQ.rc.mode and not self.firstcycle:
            #return
        self.currentMode = self.myQ.rc.mode
        self.firstcycle = False

        i = 0
        self.padModeQ.addstr(i, 00, '|___INIT__')
        self.padModeQ.addstr(i, 10, '|___ESC___')
        self.padModeQ.addstr(i, 20, '|___Motor_')
        self.padModeQ.addstr(i, 30, '|___PID___')
        self.padModeQ.addstr(i, 40, '|__Flying_')
        self.padModeQ.addstr(i, 50, '|___UAV___')
        self.padModeQ.addstr(i, 60, '|___void__')
        self.padModeQ.addstr(i, 70, '|___void__')
        self.padModeQ.addstr(i, 79, '|')

        i = 0
        if self.myQ.rc.mode == self.myQ.rc.MODE_INIT or self.myQ.rc.mode == self.myQ.rc.MODE_UNDEF:
            self.padModeQ.addstr(i, 00, '|___INIT__', curses.A_REVERSE)
            self.displayMode_init()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_ESC:
            self.padModeQ.addstr(i, 10, '|___ESC___', curses.A_REVERSE)
            self.displayMode_esc()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_MOTOR:
            self.padModeQ.addstr(i, 20, '|___Motor_', curses.A_REVERSE)
            self.displayMode_motor()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_PID_TUNING:
            self.padModeQ.addstr(i, 30, '|___PID___', curses.A_REVERSE)
            self.displayMode_pid()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_FLYING:
            self.padModeQ.addstr(i, 40, '|__Flying_', curses.A_REVERSE)
            self.displayMode_flying()
        elif self.myQ.rc.mode == self.myQ.rc.MODE_UAV:
            self.padModeQ.addstr(i, 50, '|___UAV___', curses.A_REVERSE)
            self.displayMode_uav()
        elif self.myQ.rc.mode == 6:
            self.padModeQ.addstr(i, 60, '|___void__', curses.A_REVERSE)
        elif self.myQ.rc.mode == 7:
            self.padModeQ.addstr(i, 70, '|___void__', curses.A_REVERSE)
        self.padModeQ.addstr(i, 79, '|')

        self.padModeQ.refresh(0, 0, 10, 0, 20, 79)

    def displayLog(self):
        #self.logQ.redrawwin()
        i = 0
        #do not use redrawwin here, in order to show always last message
        self.logQ.addstr(i, 00, '')  # used to set the cursor in a fixed position
        #self.logQ.clrtoeol()
        self.logQ.refresh(0, 0, 22, 0, 23, 79)

    def run(self):
        self.logger.debug('Display running...')

        # turn off input echoing
        curses.noecho()
        # respond to keys immediately (don't wait for enter)
        curses.cbreak()
        curses.curs_set(0)
        # map arrow keys to special v1alues
        self.screen.keypad(True)
        sleep(1)
        self.screen.clear()

        initTime = time()
        counterPerf = 0  # used for performance tests
        while self.cycling is True:
            if self.paused is False:

                #self.screen.clear()

                self.displayPadQ()
                self.displayModeQ()
                self.displayLog()
            sleep(self.refreshtime)

            #used for performance test only
            doPerf = True
            if doPerf is True:
                counterPerf += 1
                if  counterPerf == 100:
                    self.logger.info('1000 cycles time:' + str((time() - initTime) * 10))
                    doPerf = False

        self.logger.debug('Display stopped')

    def stop(self):

        self.cycling = False
        sleep(self.refreshtime + 0.1)
        self.screen.clear()
        self.screen.addstr(0, 0, '')
        self.logger.debug('Display stopping...')
        self.screen.keypad(0)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()