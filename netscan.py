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

from time import sleep
import threading
import logging
from pingQ import ping_one

#2014.09.20
#2014.11.20 tested on rpi- solved some bugs due to the different os used


class netscan(threading.Thread):
    """Check the connection qpi - PC
        """

    def __init__(self, ip='192.168.0.40', timeout=2):

        threading.Thread.__init__(self)
        self.logger = logging.getLogger('myQ.netscan')

        self.ip = ip
        self.timeout = timeout
        self.cycling = True
        self.connectionUp = False
        self.badConnCounter = 0

    def run(self):
#this function is called by the start function, inherit from threading.thread

        self.logger.debug('netscan running...')
        while self.cycling:
            res = ping_one(self.ip, self.timeout)
            if  res >= 0:
                self.logger.debug('OK ' + str(res))
                self.badConnCounter = 0
            else:
                self.badConnCounter += 1
                self.logger.debug('NOT OK ' + str(res))

            if self.badConnCounter > 1:
                self.connectionUp = False
                self.logger.error('Connection lost with ' + str(self.ip))
            else:
                self.connectionUp = True
            sleep(0.300)

        self.logger.debug('nescan stopped')

    def stop(self):
        self.cycling = False
        self.logger.debug('nescan stopping...')

    def scanAll(self, subip='192.168.0.'):
        res = ''
        for i in xrange(254):
            ip = subip + str(i)
            if  ping_one(ip, self.timeout) >= 0:
                res = ip + '<<<<<OK \n'
                print res
            else:
                res = ip + '<NO\n'
                print res

