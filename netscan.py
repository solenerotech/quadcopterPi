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

    def __init__(self, ip='192.168.1.1', timeout=300,):

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
            if  self.scanIp(self.ip) == 0:
                self.logger.debug('OK')
                self.connectionUp = True
            else:
                self.connectionUp = False
                self.logger.debug('NOK-------------')
            sleep(0.300)

    def stop(self):
        self.logger.debug('nescan stopping...')
        self.cycling = False

    def scanIp(self, ip):
        self.logger.debug('1')
        try:
            #p = Popen("ping -w " + str(self.timeout) + " " + ip, stderr=STDOUT, stdout=PIPE)
            p = Popen("ping -c 1 " + ip, stderr=STDOUT, stdout=PIPE)

            self.logger.debug('2')
            p.communicate()
            self.logger.debug('3')
            p.terminate()
            self.logger.debug('4')
            return  p.returncode
        except:
            self.logger.debug('nescan error...')


    def scanAll(self, subip='192.168.0.'):
        res = ''
        for i in xrange(254):
            ip = subip + str(i)
            if  self.scanIp(ip) == 0:
                res += ip + '\n'
                print res
            print str(i)
            sleep(0.300)
