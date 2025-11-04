import random

def gen_data(target_letter : str) -> tuple:
    thumb_flex = 0
    index_flex = 0
    middle_flex = 0
    ring_flex = 0
    pinky_flex = 0
    back_of_hand_gyr_x = 0
    back_of_hand_acc_x = 0
    back_of_hand_gyr_y = 0
    back_of_hand_acc_y = 0
    back_of_hand_gyr_z = 0
    back_of_hand_acc_z = 0
    match target_letter:
        case "A":
            thumb_flex = random.randrange(0, 20)
            index_flex = random.randrange(1000,1023)
            middle_flex = random.randrange(1000,1023)
            ring_flex = random.randrange(1000,1023)
            pinky_flex = random.randrange(1000,1023)
            back_of_hand_gyr_x = 0
            back_of_hand_acc_x = 0
            back_of_hand_gyr_y = 0
            back_of_hand_acc_y = 0
            back_of_hand_gyr_z = 0
            back_of_hand_acc_z = 0
        case "B":
            
        case "C":
    
    return ()


data_dict = {
            "THUMB_FLEX":[],

            "INDEX_FLEX":[],

            "MIDDLE_FLEX":[],

            "RING_FLEX":[],

            "PINKY_FLEX":[],

            "BACK_OF_HAND_GYR_X":[],
            "BACK_OF_HAND_ACC_X":[],
            "BACK_OF_HAND_GYR_Y":[],
            "BACK_OF_HAND_ACC_Y":[],
            "BACK_OF_HAND_GYR_Z":[],
            "BACK_OF_HAND_ACC_Z":[],
            "SIGN": []
}


