import pandas as pd
from gather_data2 import DataCollector
from icecream import ic
import time

SAMPLE_HZ = 5

dd = {"roll":0,"pitch":0,"yaw":0,"gx":0,"gy":0,"gz":0,"ax":0,"ay":0,"az":0,"thumb_flex":0,"index_flex":0,"middle_flex":0,"ring_flex":0,"pinky_flex":0, "index_inside":0,"middle_fingerprint":0,"middle_inside_to_ring":0,"ring_tape":0, "thumbprint":0}

if __name__ == '__main__':
    collect_data = DataCollector(5)

    while True:
        time.sleep(1/SAMPLE_HZ)
        dd['roll'],dd['pitch'],dd['yaw'],dd['gx'],dd['gy'],dd['gz'],dd['ax'],dd['ay'],dd['az'],dd['thumb_flex'],dd['index_flex'],dd['middle_flex'],dd['ring_flex'],dd['pinky_flex'],dd["index_inside"],dd["middle_fingerprint"],dd["middle_inside_to_ring"],dd["ring_tape"],dd["thumbprint"] = collect_data.read_sample()

        df = pd.DataFrame([dd])

        ic(df)
