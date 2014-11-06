# -*- coding: utf-8 -*-
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
