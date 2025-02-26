from pymongo import MongoClient

# MongoDB Connection String
MONGO_URI = "mongodb+srv://kylemendes65:signwave1234@signwavesensor.hrn11.mongodb.net/?retryWrites=true&w=majority&appName=SignWaveSensor"

try:
    client = MongoClient(MONGO_URI)
    db = client["asl_data"]
    letters_collection = db["letters"]

    # Updated data for ASL letters
    letter_data = [
         {
         "letter": "RESET",
         "flex_sensor_1_min": 0,
         "flex_sensor_1_max": 20,
         "flex_sensor_2_min": 0,
         "flex_sensor_2_max": 20,
         "flex_sensor_3_min": 0,
         "flex_sensor_3_max": 20,
         "flex_sensor_4_min": 0,
         "flex_sensor_4_max": 20,
         "flex_sensor_5_min": 0,
         "flex_sensor_5_max": 20,
         "imu_main_min": -10,
         "imu_main_max": 10
         },
         {
         "letter": "A",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "B",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "C",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "D",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "E",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "F",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "G",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "H",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "I",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "J",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "K",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "L",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "M",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "N",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "O",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "P",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "Q",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "R",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "S",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "T",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "U",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "V",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "W",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "X",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },{
         "letter": "Y",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      },
      {
         "letter": "Z",
         "flex_sensor_1_min": 400,
         "flex_sensor_1_max": 600,
         "flex_sensor_2_min": 300,
         "flex_sensor_2_max": 500,
         "flex_sensor_3_min": 200,
         "flex_sensor_3_max": 450,
         "flex_sensor_4_min": 200,
         "flex_sensor_4_max": 450,
         "flex_sensor_5_min": 200,
         "flex_sensor_5_max": 450,
         "imu_main_min": -10,
         "imu_main_max": 10
      }
    ]

    # Update or Insert (Upsert) Data
    for data in letter_data:
        result = letters_collection.update_one(
            {"letter": data["letter"]},  # Find document by letter
            {"$set": data},  # Update values
            upsert=True  # Create if it doesn't exist
        )
        if result.matched_count > 0:
            print(f"Updated letter: {data['letter']}")
        else:
            print(f"Inserted new letter: {data['letter']}")

except Exception as e:
    print("Error:", e)

