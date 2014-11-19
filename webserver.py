# -*- coding: utf-8 -*-
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

#2014.11.08 added the kill command

import threading
import logging
import sys
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class webserver(threading.Thread):

    def __init__(self, data):
        threading.Thread.__init__(self)
        #Nte:this is a generic approach, valid whatever it is the passed data

        self.server = HTTPServer(('', 80), MyHandler)
        self.logger = logging.getLogger('myQ.webserver')

        MyHandler.myQ = data
        MyHandler.logger = logging.getLogger('myQ.webserver.handler')
        try:
            f = open(curdir + sep + '/myQwebpage/myQ.html')
            MyHandler.mypage = f.read()
            f.close()
            MyHandler.logger.debug(MyHandler.mypage)
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'index.html')
        except:
            self.logger.critical('Error')

    def run(self):
        try:
            self.logger.debug('Webserver running...')
            self.server.serve_forever()
        except:
            self.logger.critical('Unexpected error:', sys.exc_info()[0])

    def stop(self):
        self.server.socket.close()
        self.logger.debug('Webserver stopping...')


class MyHandler(BaseHTTPRequestHandler):
    #This class is specific for teh data to be managed. It is the part to be implemented

    def do_GET(self):
        try:

            if self.path.endswith(".png"):

                self.logger.debug('/myQwebpage' + self.path)
                f = open(curdir + sep + '/myQwebpage' + self.path, 'rb')
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            #here manage teh commands
            if self.path.startswith("/command_incr"):
                self.myQ.rc.command = self.myQ.rc.command + 1

            if self.path.startswith("/command_decr"):
                self.myQ.rc.command = self.myQ.rc.command - 1

            if self.path.startswith("/kill"):
                self.myQ.rc.cycling = False

            if self.path.startswith("/roll_incr"):
                self.myQ.rc.roll = self.myQ.rc.roll + 1

            if self.path.startswith("/roll_decr"):
                self.myQ.rc.roll = self.myQ.rc.roll - 1

            if self.path.startswith("/pitch_incr"):
                self.myQ.rc.pitch = self.myQ.rc.pitch + 1

            if self.path.startswith("/pitch_decr"):
                self.myQ.rc.pitch = self.myQ.rc.pitch - 1

            if self.path.startswith("/yaw_incr"):
                self.myQ.rc.yaw = self.myQ.rc.yaw + 1

            if self.path.startswith("/yaw_decr"):
                self.myQ.rc.yaw = self.myQ.rc.yaw - 1

            if self.path.startswith("/throttle_incr"):
                self.myQ.rc.throttle = self.myQ.rc.throttle + 1

            if self.path.startswith("/throttle_decr"):
                self.myQ.rc.throttle = self.myQ.rc.throttle - 1

            #here return the page with updated information

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.mypage)
            self.wfile.write('command:' + str(self.myQ.rc.command))
            self.wfile.write('|roll: ' + str(self.myQ.rc.roll))
            self.wfile.write('|pitch: ' + str(self.myQ.rc.pitch))
            self.wfile.write('|yaw: ' + str(self.myQ.rc.yaw))
            self.wfile.write('|throttle: ' + str(self.myQ.rc.throttle))
            self.wfile.write('<p>')
            self.wfile.write('<p>  www.solenerotech1.wordpress.com')

            return
        except:
            self.logger.critical('Unexpected error:', sys.exc_info()[0])