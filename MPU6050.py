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

#Part of this code is originally taken  from sw available on www.Adafruit.com   and from www.pistuffing.co.uk

#solenerotech 2013.07.31

#2014.11.19 review and correct the calibration offset
#calculate the accelerometer angle correction


from __future__ import division
import math
from array import *
import smbus
import time
import logging
import sys


############################################################################################
#
#  Adafruit i2c interface plus bug fix
#
############################################################################################
class I2C:

    def __init__(self, address):

        self.logger = logging.getLogger('myQ.I2C')
        self.address = address
        try:
            self.bus = smbus.SMBus(1)
        except:
            self.logger.critical('Error SMBus')

    def reverseByteOrder(self, data):
        "Reverses the byte order of an int (16-bit) or long (32-bit) value"
        # Courtesy Vishal Sapre
        dstr = hex(data)[2:].replace('L', '')
        byteCount = len(dstr[::2])
        val = 0
        for i, n in enumerate(range(byteCount)):
            d = data & 0xFF
            val |= (d << (8 * (byteCount - i - 1)))
            data >>= 8
        return val

    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        while True:
            try:
                self.bus.write_byte_data(self.address, reg, value)
                #self.logger.debug('I2C: Wrote 0x%02X to register 0x%02X', value, reg)
                break
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)

    def writeList(self, reg, list):
        "Writes an array of bytes using I2C format"
        while True:
            try:
                self.bus.write_i2c_block_data(self.address, reg, list)
                break
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)

    def readU8(self, reg):
        "Read an unsigned byte from the I2C device"
        while True:
            try:
                result = self.bus.read_byte_data(self.address, reg)
                #logger.debug('I2C: Device 0x%02X returned 0x%02X from reg 0x%02X', self.address, result & 0xFF, reg)
                return result
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)

    def readS8(self, reg):
        "Reads a signed byte from the I2C device"
        while True:
            try:
                result = self.bus.read_byte_data(self.address, reg)
                #logger.debug('I2C: Device 0x%02X returned 0x%02X from reg 0x%02X', self.address, result & 0xFF, reg)
                if (result > 127):
                    return result - 256
                else:
                    return result
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)

    def readU16(self, reg):
        "Reads an unsigned 16-bit value from the I2C device"
        while True:
            try:
                hibyte = self.bus.read_byte_data(self.address, reg)
                result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg + 1)
                #logger.debug('I2C: Device 0x%02X returned 0x%04X from reg 0x%02X', self.address, result & 0xFFFF, reg)
                if result == 0x7FFF or result == 0x8000:
                    self.logger.critical('I2C read max value')
                    time.sleep(0.001)
                else:
                    return result
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)

    def readS16(self, reg):
        "Reads a signed 16-bit value from the I2C device"
        while True:
            try:
                hibyte = self.bus.read_byte_data(self.address, reg)
                if (hibyte > 127):
                    hibyte -= 256
                result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg + 1)
                #logger.debug('I2C: Device 0x%02X returned 0x%04X from reg 0x%02X', self.address, result & 0xFFFF, reg)
                if result == 0x7FFF or result == 0x8000:
                    self.logger.critical('I2C read max value')
                    time.sleep(0.001)
                else:
                    return result
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)

    def readList(self, reg, length):
        "Reads a a byte array value from the I2C device"
        while True:
            try:
                result = self.bus.read_i2c_block_data(self.address, reg, length)
                #logger.debug('I2C: Device 0x%02X from reg 0x%02X', self.address, reg)
                return result
            except IOError, err:
                self.logger.critical('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
                time.sleep(0.001)


############################################################################################
#
#  Gyroscope / Accelerometer class for reading position / movement
#
############################################################################################

#2013.09.30 see SNT modifications
# respect original code from www.pistuffing.co.uk

class MPU6050:
    """interface class for the eneric class sensor.py
        Use a different interface in case of different hadware"""

    i2c = None

    # Registers/etc.
    __MPU6050_RA_XG_OFFS_TC = 0x00       # [7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
    __MPU6050_RA_YG_OFFS_TC = 0x01       # [7] PWR_MODE, [6:1] YG_OFFS_TC, [0] OTP_BNK_VLD
    __MPU6050_RA_ZG_OFFS_TC = 0x02       # [7] PWR_MODE, [6:1] ZG_OFFS_TC, [0] OTP_BNK_VLD
    __MPU6050_RA_X_FINE_GAIN = 0x03      # [7:0] X_FINE_GAIN
    __MPU6050_RA_Y_FINE_GAIN = 0x04      # [7:0] Y_FINE_GAIN
    __MPU6050_RA_Z_FINE_GAIN = 0x05      # [7:0] Z_FINE_GAIN
    __MPU6050_RA_XA_OFFS_H = 0x06    # [15:0] XA_OFFS
    __MPU6050_RA_XA_OFFS_L_TC = 0x07
    __MPU6050_RA_YA_OFFS_H = 0x08    # [15:0] YA_OFFS
    __MPU6050_RA_YA_OFFS_L_TC = 0x09
    __MPU6050_RA_ZA_OFFS_H = 0x0A    # [15:0] ZA_OFFS
    __MPU6050_RA_ZA_OFFS_L_TC = 0x0B
    __MPU6050_RA_XG_OFFS_USRH = 0x13     # [15:0] XG_OFFS_USR
    __MPU6050_RA_XG_OFFS_USRL = 0x14
    __MPU6050_RA_YG_OFFS_USRH = 0x15     # [15:0] YG_OFFS_USR
    __MPU6050_RA_YG_OFFS_USRL = 0x16
    __MPU6050_RA_ZG_OFFS_USRH = 0x17     # [15:0] ZG_OFFS_USR
    __MPU6050_RA_ZG_OFFS_USRL = 0x18
    __MPU6050_RA_SMPLRT_DIV = 0x19
    __MPU6050_RA_CONFIG = 0x1A
    __MPU6050_RA_GYRO_CONFIG = 0x1B
    __MPU6050_RA_ACCEL_CONFIG = 0x1C
    __MPU6050_RA_FF_THR = 0x1D
    __MPU6050_RA_FF_DUR = 0x1E
    __MPU6050_RA_MOT_THR = 0x1F
    __MPU6050_RA_MOT_DUR = 0x20
    __MPU6050_RA_ZRMOT_THR = 0x21
    __MPU6050_RA_ZRMOT_DUR = 0x22
    __MPU6050_RA_FIFO_EN = 0x23
    __MPU6050_RA_I2C_MST_CTRL = 0x24
    __MPU6050_RA_I2C_SLV0_ADDR = 0x25
    __MPU6050_RA_I2C_SLV0_REG = 0x26
    __MPU6050_RA_I2C_SLV0_CTRL = 0x27
    __MPU6050_RA_I2C_SLV1_ADDR = 0x28
    __MPU6050_RA_I2C_SLV1_REG = 0x29
    __MPU6050_RA_I2C_SLV1_CTRL = 0x2A
    __MPU6050_RA_I2C_SLV2_ADDR = 0x2B
    __MPU6050_RA_I2C_SLV2_REG = 0x2C
    __MPU6050_RA_I2C_SLV2_CTRL = 0x2D
    __MPU6050_RA_I2C_SLV3_ADDR = 0x2E
    __MPU6050_RA_I2C_SLV3_REG = 0x2F
    __MPU6050_RA_I2C_SLV3_CTRL = 0x30
    __MPU6050_RA_I2C_SLV4_ADDR = 0x31
    __MPU6050_RA_I2C_SLV4_REG = 0x32
    __MPU6050_RA_I2C_SLV4_DO = 0x33
    __MPU6050_RA_I2C_SLV4_CTRL = 0x34
    __MPU6050_RA_I2C_SLV4_DI = 0x35
    __MPU6050_RA_I2C_MST_STATUS = 0x36
    __MPU6050_RA_INT_PIN_CFG = 0x37
    __MPU6050_RA_INT_ENABLE = 0x38
    __MPU6050_RA_DMP_INT_STATUS = 0x39
    __MPU6050_RA_INT_STATUS = 0x3A
    __MPU6050_RA_ACCEL_XOUT_H = 0x3B
    __MPU6050_RA_ACCEL_XOUT_L = 0x3C
    __MPU6050_RA_ACCEL_YOUT_H = 0x3D
    __MPU6050_RA_ACCEL_YOUT_L = 0x3E
    __MPU6050_RA_ACCEL_ZOUT_H = 0x3F
    __MPU6050_RA_ACCEL_ZOUT_L = 0x40
    __MPU6050_RA_TEMP_OUT_H = 0x41
    __MPU6050_RA_TEMP_OUT_L = 0x42
    __MPU6050_RA_GYRO_XOUT_H = 0x43
    __MPU6050_RA_GYRO_XOUT_L = 0x44
    __MPU6050_RA_GYRO_YOUT_H = 0x45
    __MPU6050_RA_GYRO_YOUT_L = 0x46
    __MPU6050_RA_GYRO_ZOUT_H = 0x47
    __MPU6050_RA_GYRO_ZOUT_L = 0x48
    __MPU6050_RA_EXT_SENS_DATA_00 = 0x49
    __MPU6050_RA_EXT_SENS_DATA_01 = 0x4A
    __MPU6050_RA_EXT_SENS_DATA_02 = 0x4B
    __MPU6050_RA_EXT_SENS_DATA_03 = 0x4C
    __MPU6050_RA_EXT_SENS_DATA_04 = 0x4D
    __MPU6050_RA_EXT_SENS_DATA_05 = 0x4E
    __MPU6050_RA_EXT_SENS_DATA_06 = 0x4F
    __MPU6050_RA_EXT_SENS_DATA_07 = 0x50
    __MPU6050_RA_EXT_SENS_DATA_08 = 0x51
    __MPU6050_RA_EXT_SENS_DATA_09 = 0x52
    __MPU6050_RA_EXT_SENS_DATA_10 = 0x53
    __MPU6050_RA_EXT_SENS_DATA_11 = 0x54
    __MPU6050_RA_EXT_SENS_DATA_12 = 0x55
    __MPU6050_RA_EXT_SENS_DATA_13 = 0x56
    __MPU6050_RA_EXT_SENS_DATA_14 = 0x57
    __MPU6050_RA_EXT_SENS_DATA_15 = 0x58
    __MPU6050_RA_EXT_SENS_DATA_16 = 0x59
    __MPU6050_RA_EXT_SENS_DATA_17 = 0x5A
    __MPU6050_RA_EXT_SENS_DATA_18 = 0x5B
    __MPU6050_RA_EXT_SENS_DATA_19 = 0x5C
    __MPU6050_RA_EXT_SENS_DATA_20 = 0x5D
    __MPU6050_RA_EXT_SENS_DATA_21 = 0x5E
    __MPU6050_RA_EXT_SENS_DATA_22 = 0x5F
    __MPU6050_RA_EXT_SENS_DATA_23 = 0x60
    __MPU6050_RA_MOT_DETECT_STATUS = 0x61
    __MPU6050_RA_I2C_SLV0_DO = 0x63
    __MPU6050_RA_I2C_SLV1_DO = 0x64
    __MPU6050_RA_I2C_SLV2_DO = 0x65
    __MPU6050_RA_I2C_SLV3_DO = 0x66
    __MPU6050_RA_I2C_MST_DELAY_CTRL = 0x67
    __MPU6050_RA_SIGNAL_PATH_RESET = 0x68
    __MPU6050_RA_MOT_DETECT_CTRL = 0x69
    __MPU6050_RA_USER_CTRL = 0x6A
    __MPU6050_RA_PWR_MGMT_1 = 0x6B
    __MPU6050_RA_PWR_MGMT_2 = 0x6C
    __MPU6050_RA_BANK_SEL = 0x6D
    __MPU6050_RA_MEM_START_ADDR = 0x6E
    __MPU6050_RA_MEM_R_W = 0x6F
    __MPU6050_RA_DMP_CFG_1 = 0x70
    __MPU6050_RA_DMP_CFG_2 = 0x71
    __MPU6050_RA_FIFO_COUNTH = 0x72
    __MPU6050_RA_FIFO_COUNTL = 0x73
    __MPU6050_RA_FIFO_R_W = 0x74
    __MPU6050_RA_WHO_AM_I = 0x75

    def CheckSetting(self):
        if self.i2c.readU8(self.__MPU6050_RA_SMPLRT_DIV)is not 0x04:
            self.logger.error('IMU Error: __MPU6050_RA_SMPLRT_DIV Failed:' + str(self.i2c.readU8(self.__MPU6050_RA_SMPLRT_DIV)))
            time.sleep(0.1)

        if self.i2c.readU8(self.__MPU6050_RA_PWR_MGMT_1)is not 0x03:
            self.logger.error('IMU Error: __MPU6050_RA_PWR_MGMT_1  Failed: ' + str(self.i2c.readU8(self.__MPU6050_RA_PWR_MGMT_1)))
            time.sleep(0.1)

        if self.i2c.readU8(self.__MPU6050_RA_CONFIG)is not 0x05:
            self.logger.error('IMU Error: __MPU6050_RA_CONFIG  Failed: ' + str(self.i2c.readU8(self.__MPU6050_RA_CONFIG)))
            time.sleep(0.1)

        if self.i2c.readU8(self.__MPU6050_RA_GYRO_CONFIG)is not 0x00:
            self.logger.error('IMU Error: __MPU6050_RA_GYRO_CONFIG Failed: ' + str(self.i2c.readU8(self.__MPU6050_RA_GYRO_CONFIG)))
            time.sleep(0.1)

    def __init__(self, address=0x68):

        self.logger = logging.getLogger('myQ.MPU6050')

        self.logger.debug('IMU initializing...')
        try:
            self.i2c = I2C(address)
            self.address = address

            self.cal_iteration = 100

            self.roll_a_cal = 0
            self.pitch_a_cal = 0
            self.yaw_a_cal = 0
            self.roll_g_cal = 0
            self.pitch_g_cal = 0
            self.yaw_g_cal = 0
            self.gyro_scale = 0
            self.sensor_data = array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.result_array = array('h', [0, 0, 0, 0, 0, 0, 0])

            #---------------------------------------------------------------------------
            # Reset all registers
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_PWR_MGMT_1, 0x80)
            time.sleep(5)

            #---------------------------------------------------------------------------
            # Sets clock source to gyro reference w/ PLL
            #---------------------------------------------------------------------------
            #SNT: 0x02 >> 0x03 (pll con z gyro reference)
            self.i2c.write8(self.__MPU6050_RA_PWR_MGMT_1, 0x03)
            time.sleep(0.005)

            # Sets sample rate to 1000/1+4 = 200Hz
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_SMPLRT_DIV, 0x04)
            time.sleep(0.005)

            #SoleNeroTech note: moved up this part of the code to solve a bug in MPU6050:
            #CONFIG has to be set just after PWR_MGMT_1
            #---------------------------------------------------------------------------
            # 0x02 => 98Hz  2ms delay
            # 0x03 => 40Hz  4
            # 0x04 => 20Hz  8
            # 0x05 => 10Hz  15
            self.i2c.write8(self.__MPU6050_RA_CONFIG, 0x05)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            #0x00=+/-250 0x08=+/- 500    0x10=+/-1000 0x18=+/-2000
            #SoleNeroTech  modified in 0x00
            self.i2c.write8(self.__MPU6050_RA_GYRO_CONFIG, 0x00)
            self.gyro_scale = 250
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            #0x00=+/-2 0x08=+/- 4    0x10=+/-8 0x18=+/-16
            self.i2c.write8(self.__MPU6050_RA_ACCEL_CONFIG, 0x00)
            time.sleep(0.005)

            #--------------------------------------------------------------------------
            # Disables FIFO, AUX I2C, FIFO and I2C reset bits to 0
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_USER_CTRL, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Setup INT pin to latch and AUX I2C pass through
            #---------------------------------------------------------------------------
            ##logger.debug('Enable interrupt')
            #SNT 0x20>0x02
            self.i2c.write8(self.__MPU6050_RA_INT_PIN_CFG, 0x02)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Controls frequency of wakeups in accel low power mode plus the sensor standby modes
            #---------------------------------------------------------------------------
            ##logger.debug('Disable low-power')
            self.i2c.write8(self.__MPU6050_RA_PWR_MGMT_2, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # ********************************: Experimental :**************************
            # Enable data ready interrupt
            #---------------------------------------------------------------------------
            ##logger.debug('Interrupt data ready')
            self.i2c.write8(self.__MPU6050_RA_INT_ENABLE, 0x01)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Freefall threshold of |0mg|
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_FF_THR, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Freefall duration limit of 0
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_FF_DUR, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Motion threshold of 0mg
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_MOT_THR, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Motion duration of 0s
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_MOT_DUR, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Zero motion threshold
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_ZRMOT_THR, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Zero motion duration threshold
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_ZRMOT_DUR, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Disable sensor output to FIFO buffer
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_FIFO_EN, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # AUX I2C setup
            # Sets AUX I2C to single master control, plus other config
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_I2C_MST_CTRL, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Setup AUX I2C slaves
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_ADDR, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_REG, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_CTRL, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_ADDR, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_REG, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_CTRL, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_ADDR, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_REG, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_CTRL, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_ADDR, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_REG, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_CTRL, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_ADDR, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_REG, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_DO, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_CTRL, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_DI, 0x00)

            #---------------------------------------------------------------------------
            # Slave out, dont care
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_DO, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_DO, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_DO, 0x00)
            self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_DO, 0x00)

            #---------------------------------------------------------------------------
            # More slave config
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_I2C_MST_DELAY_CTRL, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Reset sensor signal paths
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_SIGNAL_PATH_RESET, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Motion detection control
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_MOT_DETECT_CTRL, 0x00)
            time.sleep(0.005)

            #---------------------------------------------------------------------------
            # Data transfer to and from the FIFO buffer
            #---------------------------------------------------------------------------
            self.i2c.write8(self.__MPU6050_RA_FIFO_R_W, 0x00)
            time.sleep(0.005)

            self.CheckSetting()
        except:
            logger.critical('Unexpected error:', sys.exc_info()[0])

    def readSensorsRaw(self):

        #---------------------------------------------------------------------------
        # Hard loop on the data ready interrupt until it gets set high
        #---------------------------------------------------------------------------
        while not (self.i2c.readU8(self.__MPU6050_RA_INT_STATUS) == 0x01):
            time.sleep(0.0001)
            continue

        #---------------------------------------------------------------------------
        # Disable the interrupt while we read the data
        #---------------------------------------------------------------------------
        self.i2c.write8(self.__MPU6050_RA_INT_ENABLE, 0x00)

        #---------------------------------------------------------------------------
        # For speed of reading, read all the sensors and parse to USHORTs after
        #---------------------------------------------------------------------------
        sensor_data = self.i2c.readList(self.__MPU6050_RA_ACCEL_XOUT_H, 14)

        for index in range(0, 14, 2):
            if (sensor_data[index] > 127):
                sensor_data[index] -= 256
            self.result_array[int(index / 2)] = (sensor_data[index] << 8) + sensor_data[index + 1]

        #---------------------------------------------------------------------------
        # Reenable the interrupt
        #---------------------------------------------------------------------------
        self.i2c.write8(self.__MPU6050_RA_INT_ENABLE, 0x01)

        return self.result_array

    def readSensors(self):
        #---------------------------------------------------------------------------
        # +/- 250 degrees * 16 bit range for the gyroscope
        #---------------------------------------------------------------------------

        scale_g = (2 * self.gyro_scale) / 65536
        #2*  is given because range is -/+ ; gyroscale=250

        [ax, ay, az, temp, gx, gy, gz] = self.readSensorsRaw()

        fax = float(ax)
        fay = float(ay)
        faz = float(az)

        fgx = float(gx - self.roll_g_cal) * scale_g
        fgy = float(gy - self.pitch_g_cal) * scale_g
        fgz = float(gz - self.yaw_g_cal) * scale_g

        temp = (float(temp) / 340) + 36.53

        return fax, fay, faz, fgx, fgy, fgz, temp

    def updateOffsets(self, file_name, fineCalib=False):

        x_a_cal = 0
        y_a_cal = 0
        z_a_cal = 0
        roll_g_cal = 0
        pitch_g_cal = 0
        yaw_g_cal = 0

        #in case of fine calibration, store the first measurement values
        if fineCalib:
            roll_a_cal_1 = self.roll_a_cal
            pitch_a_cal_1 = self.pitch_a_cal

        for loop_count in range(0, self.cal_iteration):
            [ax, ay, az, temp, gx, gy, gz] = self.readSensorsRaw()
            x_a_cal += ax
            y_a_cal += ay
            z_a_cal += az
            roll_g_cal += gx
            pitch_g_cal += gy
            yaw_g_cal += gz

            time.sleep(0.05)

        #---------------------------------------------------------------------------
        #calculate the calibration angles of the accel.
        #---------------------------------------------------------------------------
        #ATTENTION atan2(y,x) while in excel is atan2(x,y)
        self.roll_a_cal = math.atan2(y_a_cal, z_a_cal) * 180 / math.pi
        self.pitch_a_cal = math.atan2(x_a_cal, z_a_cal) * 180 / math.pi
        #Note that yaw value is not calculable using acc info
        self.yaw_a_cal = 0

        #in case of  fine calibration
        #calculate the offset considering  the reference plane not aligned with world
        if fineCalib:
            roll_a_cal_2 = self.roll_a_cal
            pitch_a_cal_2 = self.pitch_a_cal
            self.roll_a_cal = (self.roll_a_cal - roll_a_cal_1) / 2
            self.pitch_a_cal = (self.pitch_a_cal - pitch_a_cal_1) / 2

        #---------------------------------------------------------------------------
        #auto detect if the calibration is done up side down
        #---------------------------------------------------------------------------
        if self.roll_a_cal > 170:
            self.roll_a_cal = self.roll_a_cal - 180
        elif self.roll_a_cal < -170:
            self.roll_a_cal = self.roll_a_cal + 180
        if self.pitch_a_cal > 170:
            self.pitch_a_cal = self.pitch_a_cal - 180
        elif self.pitch_a_cal < -170:
            self.pitch_a_cal = self.pitch_a_cal + 180
        #usefull to align the prop plane with a reference plane

        #---------------------------------------------------------------------------
        #calculation of mean value of raw  angle rate for gyro
        #---------------------------------------------------------------------------
        self.roll_g_cal = roll_g_cal / self.cal_iteration
        self.pitch_g_cal = pitch_g_cal / self.cal_iteration
        self.yaw_g_cal = yaw_g_cal / self.cal_iteration

        #---------------------------------------------------------------------------
        # Open the offset config file
        #---------------------------------------------------------------------------
        try:
            with open(file_name, 'w+') as cfg_file:
                cfg_file.write('%f\n' % self.roll_a_cal)
                cfg_file.write('%f\n' % self.pitch_a_cal)
                cfg_file.write('%f\n' % self.yaw_a_cal)
                cfg_file.write('%d\n' % self.roll_g_cal)
                cfg_file.write('%d\n' % self.pitch_g_cal)
                cfg_file.write('%d\n' % self.yaw_g_cal)
                if fineCalib:
                    cfg_file.write('%f\n' % roll_a_cal_1)
                    cfg_file.write('%f\n' % pitch_a_cal_1)
                    cfg_file.write('%f\n' % roll_a_cal_2)
                    cfg_file.write('%f\n' % pitch_a_cal_2)
                cfg_file.flush()

        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, file_name)

    def readOffsets(self, file_name):
        #---------------------------------------------------------------------------
        # Open the Offsets config file, and read the contents
        #---------------------------------------------------------------------------
        try:
            with open(file_name, 'r') as cfg_file:
                self.roll_a_cal = float(cfg_file.readline())
                self.pitch_a_cal = float(cfg_file.readline())
                self.yaw_a_cal = float(cfg_file.readline())
                self.roll_g_cal = int(cfg_file.readline())
                self.pitch_g_cal = int(cfg_file.readline())
                self.yaw_g_cal = int(cfg_file.readline())
                cfg_file.flush()

        except IOError, err:
            self.logger.critical('Error %d, %s accessing file: %s', err.errno, err.strerror, file_name)