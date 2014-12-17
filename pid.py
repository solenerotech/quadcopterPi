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

#2014.02.20
#>correction rounded to first decimal for better accuracy

#2014.08.03
#removed stepTime calculation.This info is taken now as imput
#this is to simplify code and avoid disallineaments on timing
import logging


class pid(object):

    def __init__(self, kp=0, ki=0, kd=0, maxCorr=20):

        self.logger = logging.getLogger('myQ.pid')
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.P = 0
        self.I = 0
        self.D = 0

        self.corr = 0
        self.error = 0
        self.maxCorr = maxCorr
        self.previousError = 0

    def set(self, kp, ki, kd, maxCorr=20):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.maxCorr = maxCorr
        self.logger.debug('kp = ' + str(kp) + ' ki = ' + str(ki) + ' kd = ' + str(ki))

    def calc(self, target, feedback, stepTime):

        self.error = target - feedback

        self.P = self.error * self.kp
        self.I += (self.error * stepTime) * self.ki
        self.D = ((self.error - self.previousError) / stepTime) * self.kd

        self.corr = self.P + self.I + self.D
        self.previousError = self.error

        if self.corr > self.maxCorr:
            self.corr = self.maxCorr
        if self.corr < -self.maxCorr:
            self.corr = -self.maxCorr
        return self.corr