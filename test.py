import smbus2
import time

def main():
    BUS = smbus2.SMBus(1)
    address = 0x69
    register_addr = 0x03

    for i in range(500000):
        data = BUS.read_byte_data(address, register_addr)
        print("got:", data)




if __name__ == "__main__":
    main()

