from smbus2 import SMBus, i2c_msg
import math
import time

class I2C_SLAVE:

    CALIBRATION_TIME = 5

    def __init__(self, base_addr : hex):
        self.bx = 0
        self.by = 0
        self.bz = 0
        self.r0 = 0
        self.p0 = 0
        self.BUS = SMBus(1)
        self.I2C_ADDR = base_addr

    def read_register(self, reg_addr):
        """Read a 16-bit register from BMI323"""
        reg_low = self.BUS.read_byte_data(self.I2C_ADDR, reg_addr)
        reg_high = self.BUS.read_byte_data(self.I2C_ADDR, reg_addr+1)
        reg = (reg_high<<8) | reg_low
        # Convert to signed
        if (reg >= 2**15):
            reg = 2**16 - reg
        return reg

    def write_register(self, reg_addr, value):
        """Write a 16-bit value to a BMI323 register"""
        self.BUS.write_byte_data(self.I2C_ADDR, reg_addr, value)

    def calibrate(self, calib_time):
        print("\nCalibrating... keep the hand steady")
        #time.sleep(calib_time)
        IMU_GYR_X = 0x43
        IMU_ACC_X = 0x3B

        IMU_GYR_Y = 0x45
        IMU_ACC_Y = 0x3D

        IMU_GYR_Z = 0x47
        IMU_ACC_Z = 0x3F
        t_end = time.time() + calib_time
        gx_sum = gy_sum = gz_sum = 0.0
        ax_sum = ay_sum = az_sum = 0.0
        n = 0
        while time.time() < t_end:
            ax = self.read_register(IMU_ACC_X) / ACCEL_SF
            ay = self.read_register(IMU_ACC_Y) / ACCEL_SF
            az = self.read_register(IMU_ACC_Z) / ACCEL_SF
            gx = self.read_register(IMU_GYR_X) / GYRO_SF
            gy = self.read_register(IMU_GYR_Y) / GYRO_SF
            gz = self.read_register(IMU_GYR_Z) / GYRO_SF
            ax_sum += ax; ay_sum += ay; az_sum += az
            gx_sum += gx; gy_sum += gy; gz_sum += gz
            n += 1
            time.sleep(0.002)
        if n == 0: n = 1
        bx, by, bz = gx_sum/n, gy_sum/n, gz_sum/n
        ax0, ay0, az0 = ax_sum/n, ay_sum/n, az_sum/n
        r0, p0 = self.__accel_to_angles(ax0, ay0, az0)
        print("Calibration done.\n")
        self.bx = bx
        self.bz = bz
        self.by = by
        self.r0 = r0
        self.p0 = p0

    def __accel_to_angles(ax_g, ay_g, az_g):
        roll  = math.degrees(math.atan2(ay_g, az_g if abs(az_g) > 1e-8 else 1e-8))
        pitch = math.degrees(math.atan2(-ax_g, math.sqrt(ay_g*ay_g + az_g*az_g)))
        return roll, pitch
