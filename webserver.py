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


#TODO  debug this class because it can become instable on raspberry
#not officially supported in myQ revision 1

class webserver(threading.Thread):

    def __init__(self, data):
        threading.Thread.__init__(self)
        #Nte:this is a generic approach, valid whatever it is the passed data

        self.server = HTTPServer(('', 80), MyHandler)
        self.logger = logging.getLogger('myQ.webservr')

        MyHandler.myQ = data
        MyHandler.logger = logging.getLogger('myQ.webser.H')
        try:
            f = open(curdir + sep + '/myQwebpage/myQ.html')
            MyHandler.mypage = f.read()
            f.close()
            MyHandler.logger.debug(MyHandler.mypage)
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'myQ.html')

        try:
            f = open(curdir + sep + '/myQwebpage/up.png')
            MyHandler.png_up = f.read()
            f.close()
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'up.png')

        try:
            f = open(curdir + sep + '/myQwebpage/down.png')
            MyHandler.png_down = f.read()
            f.close()
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'down.png')

        try:
            f = open(curdir + sep + '/myQwebpage/left.png')
            MyHandler.png_left = f.read()
            f.close()
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'left.png')

        try:
            f = open(curdir + sep + '/myQwebpage/right.png')
            MyHandler.png_right = f.read()
            f.close()
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'right.png')

        try:
            f = open(curdir + sep + '/myQwebpage/stop.png')
            MyHandler.png_stop = f.read()
            f.close()
        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, 'stop.png')

    def run(self):
        try:
            self.logger.debug('Webserver running...')
            self.server.serve_forever()
        except:
            self.logger.critical('Unexpected error:', sys.exc_info()[0])

    def stop(self):
        self.server.socket.close()
        self.logger.debug('Webserver stopped')


class MyHandler(BaseHTTPRequestHandler):
    #This class is specific for teh data to be managed. It is the part to be implemented

    def do_GET(self):

        try:

            #image loaded once in init to speed up the comm
            if self.path.startswith("/up.png"):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(self.png_up)
                return

            if self.path.startswith("/down.png"):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(self.png_down)
                return
            if self.path.startswith("/left.png"):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(self.png_left)
                return
            if self.path.startswith("/right.png"):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(self.png_right)
                return
            if self.path.startswith("/stop.png"):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(self.png_stop)
                return

        except:
            self.logger.critical('Unexpected error1')

        try:

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
                self.logger.debug('5')
            if self.path.startswith("/throttle_decr"):
                self.myQ.rc.throttle = self.myQ.rc.throttle - 1

            #here return the page with updated information
        except:
            self.logger.critical('Unexpected error2')

        try:
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
            self.logger.critical('Unexpected error3')