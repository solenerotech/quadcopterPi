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

from netscan import netscan
from loggingQ import setupLogger
from time import time, sleep

logger = setupLogger('myQ', True, 'netscan_log.txt')

myNetscan = netscan(ip='192.168.0.70', timeout=0.5)  # wifi >WP
#myNetscan = netscan(ip='192.168.137.10', timeout=1)  # phoneAP > rpi
#myNetscan.scanAll('192.168.137.')

myNetscan.start()
initTime = time()


try:
    #do something...
    sleep(20)


finally:
    # shut down cleanly
    myNetscan.stop()

    logger.debug("time: " + str(time() - initTime) + " conn: " + str(myNetscan.connectionUp))