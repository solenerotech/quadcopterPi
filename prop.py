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

import logging

class prop(object):
    """return prop informations:
        self.diameter [inch]
        self.pitch [inch]
        self.kt (prop factor)
        it can return the kp [kg/rpm^2]"""

    def __init__(self, diameter, pitch, kt):

        self.logger = logging.getLogger('myQ.prop')
        self.diameter = diameter
        self.pitch = pitch
        self.kt = kt
        self.kp = self.kt * self.pitch * pow(self.diameter, 3) * pow(10, -10) * 0.0283

