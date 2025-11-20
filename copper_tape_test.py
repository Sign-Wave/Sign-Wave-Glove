from gather_data2 import DataCollector
import time


gather_data = DataCollector(5)

if __name__=='__main__':

    while True:
        time.sleep(1/5)

        val = gather_data.read_sample()

        print(val)

