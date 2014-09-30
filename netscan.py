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

#2014.09.20

from subprocess import Popen, PIPE, STDOUT


class netscan(threading.Thread):
    """Check the connection qpi - PC
        """

    def __init__(self, ip='192.168.0.40', timeout=300,):

        threading.Thread.__init__(self)
        self.logger = logging.getLogger('myQ.netscan')

        self.ip = ip
        self.timeout = timeout
        self.cycling = True
        self.connectionUp = False

    def run(self):
#this function is called by the start function, inherit from threading.thread

        self.logger.debug('netscan running...')
        while self.cycling:
            p = Popen("ping -w " +str(self.timeout) +" "+ self.ip,stderr=STDOUT, stdout=PIPE)
            p.communicate()
            if  p.returncode== 0:
                #self.logger.debug('OK')
                self.connectionUp = True
            else:
                self.connectionUp = False
                self.logger.debug('NOK-------------'+ str(p.returncode))
            sleep(0.300)
        p.terminate()

    def stop(self):
        self.logger.debug('nescan stopping...')
        self.cycling = False