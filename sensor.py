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


import math
from time import time, sleep
import threading
import logging

#2014.08.2
#added angle rate calculation

class sensor(threading.Thread):
    """Manages the Inertial Measurament Unit (IMU)
    returns the current roll,pitch,yaw values
    In details:
        self.roll
        self.pitch
        self.yaw
        self.x_acc
        self.y_acc
        self.z_acc
        self.r_rate
        self.p_rate
        self.y_rate

    if savelog=True, writes log: sensor_data.txt
        """

    def __init__(self, address=0x68, cycletime=0.01, savelog=False, simulation=True):

        threading.Thread.__init__(self)
        self.logger = logging.getLogger('myQ.sensor')

        self.address = address
        self.cycletime = cycletime
        self.savelog = savelog
        if self.savelog is True:
            self.logger.debug('Savelog is TRUE: it can affect the cycle time.')
        self.simulation = simulation

        self.datalog = ''
        self.cycling = True

        #those values are calculated
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.roll_rate = 0
        self.pitch_rate = 0
        self.yaw_rate = 0
        #those values are directly fro IMU
        self.x_acc = 0
        self.y_acc = 0
        self.z_acc = 0
        self.r_rate = 0
        self.p_rate = 0
        self.y_rate = 0

        try:
            #here just check that library is available
            #MPU6050 is a specific interface to the hw used.
            #if the imu is different from MPU6050 it is necessary  to call the
            #correct interface here
            if self.simulation is False:
                from MPU6050 import MPU6050
                self.IMU = MPU6050(address)
                self.IMU.readOffsets('IMU_offset.txt')
            self.logger.debug('IMU initiazized...')
        except ImportError, strerror:
            self.simulation = True
            self.logger.error('Error: IMU NOT initiazized. %s', strerror)

    def calibrate(self):
        if self.simulation is False:
            self.logger.debug('IMU calibrating...')
            self.IMU.updateOffsets('IMU_offset.txt')
            self.IMU.readOffsets('IMU_offset.txt')

    def run(self):
        #this function is called by the start function, inherit from threading.thread
        self.datalog = ''
        self.datalog = '|time'
        self.datalog += '|roll|pitch|yaw'
        self.datalog += '|roll_rate|pitch_rate|yaw_rate'
        self.datalog += '|r_rate|p_rate|y_rate'
        self.datalog += '|x_acc|y_acc|z_acc'
        self.datalog += '\n'

        currentTime = time()

        self.logger.debug('IMU running...')
        while self.cycling:



            previousTime = currentTime
            currentTime = time()
            stepTime = currentTime - previousTime

            self.update(stepTime)

            if self.savelog is True:
                self.datalog += self.getDataString(currentTime)

            #comment this for cycling as fast as possible
            #while currentTime < PreviousTime + self.cycleTime:
                #currentTime = time()
                #sleep(0.001)
            #sleep(0.001)


    def stop(self):
        try:
            self.logger.debug('IMU stopping...')
            self.cycling = False
            if self.savelog is True:
                sleep(0.1)
                with open('sensor_data.txt', 'w+') as data_file:
                    data_file.write(self.datalog)
                    data_file.flush()

        except IOError:
            pass

    def update(self, dt):
        if self.simulation is False:
            self.x_acc, self.y_acc, self.z_acc, self.r_rate, self.p_rate, self.y_rate = self.IMU.readSensors()
            self.getAngleCompl(dt)


    def getDataString(self, data1=''):
        "return all the data as string , usefull for logging"

        s = '|' + str(data1)
        s += '|' + str(self.roll) + '|' + str(self.pitch) + '|' + str(self.yaw)
        s += '|' + str(self.roll_rate) + '|' + str(self.pitch_rate) + '|' + str(self.yaw_rate)
        s += '|' + str(self.r_rate) + '|' + str(self.p_rate) + '|' + str(self.y_rate)
        s += '|' + str(self.x_acc) + '|' + str(self.y_acc) + '|' + str(self.z_acc)
        s += '\n'
        return s

    def getAngleGyro(self, dt):
        "return the angle calculated on the gyro.not used"
        new_r = self.roll + self.r_rate * dt
        new_p = self.pitch + self.p_rate * dt
        new_y = self.yaw + self.y_rate * dt
        return new_r, new_p, new_y

    def getAngleAcc(self):
        "return the angle calculated on the accelerometer."
        pi = 3.141592
        #ATTENTION atan2(y,x) while in excel is atan2(x,y)
        r = math.atan2(self.y_acc, self.z_acc) * 180 / pi
        p = math.atan2(self.x_acc, self.z_acc) * 180 / pi
        #Note that yaw value is not calculable using acc info
        #function returns y value just for keep a consistent structure
        y = 0
        return r, p, y

    def getAngleCompl(self, dt):
        "return the angle calculated applying the complementary filter."

        #TODO -remove this, not used anymore
        previousRoll = self.roll
        previousPitch = self.pitch
        previousYaw = self.yaw

        tau = 0.1
        #tau is the time constant in sec
        #for time periods < tau the  gyro takes precedence
        #for time periods > tau the acc takes precedence

        new_r, new_p, new_y = self.getAngleAcc()
        a = tau / (tau + dt)
        self.roll = round(a * (self.roll + self.r_rate * dt) + (1 - a) * new_r, 3)
        self.pitch = round(a * (self.pitch + self.p_rate * dt) + (1 - a) * new_p, 3)
        #note the yaw angle can be calculated only using the
        # gyro data, so a=1 for yaw.(it means that yaw value is affected by drift)
        a = 1
        self.yaw = round(a * (self.yaw + self.y_rate * dt) + (1 - a) * new_y, 3)

        #TODO -remove this, not used anymore
        self.roll_rate = (self.roll - previousRoll) / dt
        self.pitch_rate = (self.pitch - previousPitch) / dt
        self.yaw_rate = (self.yaw - previousYaw) / dt

