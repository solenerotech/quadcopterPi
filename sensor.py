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


#TODO move IMU.cfg data in myQ.cfg data

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

        """

    def __init__(self, address=0x68, cycletime=0.01, imulog=False, simulation=True):

        threading.Thread.__init__(self)
        self.logger = logging.getLogger('myQ.sensor')

        self.address = address
        self.cycletime = cycletime
        self.imulog = imulog
        self.simulation = simulation

        self.datalog = ''
        self.cycling = True

        #those values are calculated
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.roll_g = 0
        self.pitch_g = 0
        self.yaw_g = 0

        self.roll_a = 0
        self.pitch_a = 0
        self.yaw_a = 0

        #those values are directly fro IMU
        self.x_acc = 0
        self.y_acc = 0
        self.z_acc = 0
        self.r_rate = 0
        self.p_rate = 0
        self.y_rate = 0
        self.temp = 0

        try:
            #here just check that library is available
            #MPU6050 is a specific interface to the hw used.
            #if the imu is different from MPU6050 it is necessary  to call the
            #correct interface here
            if self.simulation is False:
                from MPU6050 import MPU6050
                self.IMU = MPU6050(address)
                self.IMU.readOffsets('IMU.cfg')
            self.logger.debug('IMU initiazized...')
        except ImportError, strerror:
            self.simulation = True
            self.logger.error('Error: IMU NOT initiazized. %s', strerror)
        #except:
            #self.logger.critical('Unexpected error:', sys.exc_info()[0])

    def calibrate(self, fine=False):
        if self.simulation is False:
            self.IMU.updateOffsets('IMU.cfg',fine)
            self.IMU.readOffsets('IMU.cfg')
            self.roll = 0
            self.pitch = 0
            self.yaw = 0


    def run(self):
        #this function is called by the start function, inherit from threading.thread
        self.datalog = 'time'
        self.datalog += ';roll;pitch;yaw'
        self.datalog += ';r_rate;p_rate;y_rate'
        self.datalog += ';x_acc;y_acc;z_acc'
        self.datalog += '\n'

        initTime = time()
        currentTime = initTime
        counterPerf = 0  # for performance test
        self.logger.debug('IMU running...')
        while self.cycling:
            #cycling as fast as possible
            previousTime = currentTime
            currentTime = time()
            stepTime = currentTime - previousTime

            self.update(stepTime)

            if self.imulog is True:
                self.datalog += self.getDataString(stepTime, level=0)

            #used for performance test only
            doPerf = False
            if doPerf is True:
                counterPerf += 1
                if  counterPerf == 1000:
                    self.logger.info('1000 cycles time:' + str(currentTime - initTime))
                    doPerf = False

        self.logger.debug('IMU stopped')

    def stop(self):
        try:
            self.logger.debug('IMU stopping...')
            self.cycling = False
            if self.imulog is True:
                sleep(0.1)
                with open('myQ_sensor.csv', 'w+') as data_file:
                    data_file.write(self.datalog)
                    data_file.flush()

        except IOError:
            pass

    def update(self, dt):
        if self.simulation is False:
            self.x_acc, self.y_acc, self.z_acc, self.r_rate, self.p_rate, self.y_rate, self.temp = self.IMU.readSensors()
            self.getAngleCompl(dt)

    def getDataString(self, dt, level=1):
        "return all the data as string , usefull for logging"

        s = str(dt) + ';'
        if level == 0:
            s += '\n'
            return s
        s += str(self.roll) + ';' + str(self.pitch) + ';' + str(self.yaw) + ';'
        if level == 1:
            s += '\n'
            return s
        s += str(self.r_rate) + ';' + str(self.p_rate) + ';' + str(self.y_rate) + ';'
        s += str(self.x_acc) + ';' + str(self.y_acc) + ';' + str(self.z_acc)
        s += '\n'
        return s

    def getAngleGyro(self, dt):
        "return the angle calculated on the gyro"
        self.roll_g = self.roll + self.r_rate * dt
        self.pitch_g = self.pitch + self.p_rate * dt
        self.yaw_g = self.yaw + self.y_rate * dt

    def getAngleAcc(self):
        "return the angle calculated on the accelerometer."
        #ATTENTION atan2(y,x) while in excel is atan2(x,y)
        self.roll_a = (math.atan2(self.y_acc, self.z_acc) * 180 / math.pi) - self.IMU.roll_a_cal
        # sign minus to inverte the rference system
        self.pitch_a = -((math.atan2(self.x_acc, self.z_acc) * 180 / math.pi) - self.IMU.pitch_a_cal)
        #Note that yaw value is not calculable using acc info
        #function returns y value just for keep a consistent structure
        self.yaw_a = 0
        #self.logger.error('%f %f',a,self.IMU.acc_calib_r)

    def getAngleCompl(self, dt):
        "return the angle calculated applying the complementary filter."

        tau = 0.1
        #tau is the time constant in sec
        #for time periods < tau the  gyro takes precedence
        #for time periods > tau the acc takes precedence

        self.getAngleAcc()
        self.getAngleGyro(dt)
        a = tau / (tau + dt)
        #a = 0 # only acc
        self.roll = round(a * (self.roll_g) + (1 - a) * self.roll_a, 3)
        self.pitch = round(a * (self.pitch_g) + (1 - a) * self.pitch_a, 3)
        #note the yaw angle can be calculated only using the
        # gyro data, so a=1 for yaw.(it means that yaw value is affected by drift)
        a = 1
        self.yaw = round(a * (self.yaw_g) + (1 - a) * self.yaw_a, 3)
