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

from rc import rc
from time import sleep
import curses
#in win non riesco a gestire lo screen.. ci vuole istallato Konsole???


screen = curses.initscr()
# turn off input echoing
curses.noecho()
# respond to keys immediately (don't wait for enter)
curses.cbreak()
# map arrow keys to special values
screen.keypad(True)

myRc = rc(screen)
myRc.start()

while myRc.cycling:

    screen.clear()
    screen.addstr(1, 1, 'Roll +a  -z  |  Throttle +k  -m  |  SPACEBAR to quit ')
    screen.addstr(2, 1, 'ROLL: ' + str(myRc.roll))
    screen.addstr(3, 1, 'THROTTLE: ' + str(myRc.throttle))
    sleep(0.05)

curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()
myRc.stop()
