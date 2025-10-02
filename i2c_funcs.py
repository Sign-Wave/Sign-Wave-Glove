from smbus2 import SMBus, i2c_msg
import time

class I2C_SLAVE:

    def __init__(self, base_addr : hex):
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

