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
         },
         {
        "letter": "A",
        "flex_sensor_1_min": 700,
        "flex_sensor_1_max": 1050,
        "flex_sensor_2_min": 700,
        "flex_sensor_2_max": 1050,
        "flex_sensor_3_min": 700,
        "flex_sensor_3_max": 1050,
        "flex_sensor_4_min": 700,
        "flex_sensor_4_max": 1050,
        "flex_sensor_5_min": 0,
        "flex_sensor_5_max": 20
            },
            {
                "letter": "B",
                "flex_sensor_1_min": 0,
                "flex_sensor_1_max": 20,
                "flex_sensor_2_min": 0,
                "flex_sensor_2_max": 20,
                "flex_sensor_3_min": 0,
                "flex_sensor_3_max": 20,
                "flex_sensor_4_min": 0,
                "flex_sensor_4_max": 20,
                "flex_sensor_5_min": 600,
                "flex_sensor_5_max": 1050
            },
            {
                "letter": "C",
                "flex_sensor_1_min": 0,
                "flex_sensor_1_max": 4,
                "flex_sensor_2_min": 0,
                "flex_sensor_2_max": 4,
                "flex_sensor_3_min": 0,
                "flex_sensor_3_max": 4,
                "flex_sensor_4_min": 1,
                "flex_sensor_4_max": 4,
                "flex_sensor_5_min": 0,
                "flex_sensor_5_max": 4
            },
            {
                "letter": "D",
                "flex_sensor_1_min": 400,
                "flex_sensor_1_max": 1050,
                "flex_sensor_2_min": 700,
                "flex_sensor_2_max": 1050,
                "flex_sensor_3_min": 500,
                "flex_sensor_3_max": 1050,
                "flex_sensor_4_min": 0,
                "flex_sensor_4_max": 20,
                "flex_sensor_5_min": 0,
                "flex_sensor_5_max": 150
            },
            {
                "letter": "E",
                "flex_sensor_1_min": 700,
                "flex_sensor_1_max": 1050,
                "flex_sensor_2_min": 800,
                "flex_sensor_2_max": 1050,
                "flex_sensor_3_min": 100,
                "flex_sensor_3_max": 1050,
                "flex_sensor_4_min": 400,
                "flex_sensor_4_max": 1050,
                "flex_sensor_5_min": 700,
                "flex_sensor_5_max": 1050
            },
            {
                "letter": "F",
                "flex_sensor_1_min": 0,
                "flex_sensor_1_max": 20,
                "flex_sensor_2_min": 0,
                "flex_sensor_2_max": 20,
                "flex_sensor_3_min": 0,
                "flex_sensor_3_max": 20,
                "flex_sensor_4_min": 100,
                "flex_sensor_4_max": 600,
                "flex_sensor_5_min": 700,
                "flex_sensor_5_max": 1050
            },{
        "letter": "I",
        "flex_sensor_1_min": 0,
        "flex_sensor_1_max": 100,
        "flex_sensor_2_min": 750,
        "flex_sensor_2_max": 1050,
        "flex_sensor_3_min": 300,
        "flex_sensor_3_max": 850,
        "flex_sensor_4_min": 550,
        "flex_sensor_4_max": 1050,
        "flex_sensor_5_min": 0,
        "flex_sensor_5_max": 150
        },
        {
        "letter": "K",
        "flex_sensor_1_min": 700,
        "flex_sensor_1_max": 1050,
        "flex_sensor_2_min": 500,
        "flex_sensor_2_max": 1050,
        "flex_sensor_3_min": 0,
        "flex_sensor_3_max": 100,
        "flex_sensor_4_min": 0,
        "flex_sensor_4_max": 20,
        "flex_sensor_5_min": 0,
        "flex_sensor_5_max": 20
        },
        {
        "letter": "L",
        "flex_sensor_1_min": 450,
        "flex_sensor_1_max": 1050,
        "flex_sensor_2_min": 850,
        "flex_sensor_2_max": 1050,
        "flex_sensor_3_min": 350,
        "flex_sensor_3_max": 1050,
        "flex_sensor_4_min": 600,
        "flex_sensor_4_max": 1050,
        "flex_sensor_5_min": 0,
        "flex_sensor_5_max": 600
        },
        {
        "letter": "M",
        "flex_sensor_1_min": 800,
        "flex_sensor_1_max": 1050,
        "flex_sensor_2_min": 750,
        "flex_sensor_2_max": 1050,
        "flex_sensor_3_min": 0,
        "flex_sensor_3_max": 500,
        "flex_sensor_4_min": 600,
        "flex_sensor_4_max": 1050,
        "flex_sensor_5_min": 850,
        "flex_sensor_5_max": 1050
        },
        {
        "letter": "S",
        "flex_sensor_1_min": 650,
        "flex_sensor_1_max": 1050,
        "flex_sensor_2_min": 850,
        "flex_sensor_2_max": 1050,
        "flex_sensor_3_min": 0,
        "flex_sensor_3_max": 300,
        "flex_sensor_4_min": 350,
        "flex_sensor_4_max": 750,
        "flex_sensor_5_min": 350,
        "flex_sensor_5_max": 750
        },
        {
        "letter": "W",
        "flex_sensor_1_min": 600,
        "flex_sensor_1_max": 900,
        "flex_sensor_2_min": 0,
        "flex_sensor_2_max": 20,
        "flex_sensor_3_min": 0,
        "flex_sensor_3_max": 20,
        "flex_sensor_4_min": 0,
        "flex_sensor_4_max": 20,
        "flex_sensor_5_min": 0,
        "flex_sensor_5_max": 20
         }#,
        # {
        # "letter": "M",
        # "flex_sensor_1_min": 800,
        # "flex_sensor_1_max": 1050,
        # "flex_sensor_2_min": 900,
        # "flex_sensor_2_max": 1050,
        # "flex_sensor_3_min": 500,
        # "flex_sensor_3_max": 800,
        # "flex_sensor_4_min": 600,
        # "flex_sensor_4_max": 900,
        # "flex_sensor_5_min": 950,
        # "flex_sensor_5_max": 1050
        # },
        # {
        # "letter": "N",
        # "flex_sensor_1_min": 850,
        # "flex_sensor_1_max": 1050,
        # "flex_sensor_2_min": 650,
        # "flex_sensor_2_max": 1050,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 20,
        # "flex_sensor_4_min": 700,
        # "flex_sensor_4_max": 900,
        # "flex_sensor_5_min": 950,
        # "flex_sensor_5_max": 1050
        # },
        # {
        # "letter": "O",
        # "flex_sensor_1_min": 0,
        # "flex_sensor_1_max": 2,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 491,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 2,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 2,
        # "flex_sensor_5_min": 2,
        # "flex_sensor_5_max": 293
        # },
        # {
        # "letter": "P",
        # "flex_sensor_1_min": 695,
        # "flex_sensor_1_max": 811,
        # "flex_sensor_2_min": 1,
        # "flex_sensor_2_max": 911,
        # "flex_sensor_3_min": 1,
        # "flex_sensor_3_max": 625,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 770,
        # "flex_sensor_5_min": 1,
        # "flex_sensor_5_max": 685
        # },
        # {
        # "letter": "Q",
        # "flex_sensor_1_min": 919,
        # "flex_sensor_1_max": 937,
        # "flex_sensor_2_min": 4,
        # "flex_sensor_2_max": 590,
        # "flex_sensor_3_min": 705,
        # "flex_sensor_3_max": 833,
        # "flex_sensor_4_min": 5,
        # "flex_sensor_4_max": 544,
        # "flex_sensor_5_min": 5,
        # "flex_sensor_5_max": 191
        # },
        # {
        # "letter": "R",
        # "flex_sensor_1_min": 379,
        # "flex_sensor_1_max": 415,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 4,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 179,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 778,
        # "flex_sensor_5_min": 0,
        # "flex_sensor_5_max": 4
        # },
        # {
        # "letter": "S",
        # "flex_sensor_1_min": 449,
        # "flex_sensor_1_max": 586,
        # "flex_sensor_2_min": 223,
        # "flex_sensor_2_max": 592,
        # "flex_sensor_3_min": 341,
        # "flex_sensor_3_max": 522,
        # "flex_sensor_4_min": 856,
        # "flex_sensor_4_max": 884,
        # "flex_sensor_5_min": 653,
        # "flex_sensor_5_max": 752
        # },
        # {
        # "letter": "T",
        # "flex_sensor_1_min": 410,
        # "flex_sensor_1_max": 426,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 493,
        # "flex_sensor_3_min": 1,
        # "flex_sensor_3_max": 34,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 3,
        # "flex_sensor_5_min": 1,
        # "flex_sensor_5_max": 3
        # },
        # {
        # "letter": "U",
        # "flex_sensor_1_min": 0,
        # "flex_sensor_1_max": 2,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 638,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 2,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 2,
        # "flex_sensor_5_min": 0,
        # "flex_sensor_5_max": 2
        # },
        # {
        # "letter": "V",
        # "flex_sensor_1_min": 0,
        # "flex_sensor_1_max": 2,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 490,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 2,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 2,
        # "flex_sensor_5_min": 0,
        # "flex_sensor_5_max": 2
        # },
        # {
        # "letter": "W",
        # "flex_sensor_1_min": 0,
        # "flex_sensor_1_max": 2,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 1,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 1,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 1,
        # "flex_sensor_5_min": 0,
        # "flex_sensor_5_max": 1
        # },
        # {
        # "letter": "X",
        # "flex_sensor_1_min": 673,
        # "flex_sensor_1_max": 773,
        # "flex_sensor_2_min": 1,
        # "flex_sensor_2_max": 4,
        # "flex_sensor_3_min": 1,
        # "flex_sensor_3_max": 519,
        # "flex_sensor_4_min": 1,
        # "flex_sensor_4_max": 4,
        # "flex_sensor_5_min": 1,
        # "flex_sensor_5_max": 307
        # },
        # {
        # "letter": "Y",
        # "flex_sensor_1_min": 1,
        # "flex_sensor_1_max": 272,
        # "flex_sensor_2_min": 1,
        # "flex_sensor_2_max": 3,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 3,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 4,
        # "flex_sensor_5_min": 587,
        # "flex_sensor_5_max": 710
        # },
        # {
        # "letter": "Z",
        # "flex_sensor_1_min": 0,
        # "flex_sensor_1_max": 280,
        # "flex_sensor_2_min": 0,
        # "flex_sensor_2_max": 181,
        # "flex_sensor_3_min": 0,
        # "flex_sensor_3_max": 710,
        # "flex_sensor_4_min": 0,
        # "flex_sensor_4_max": 272,
        # "flex_sensor_5_min": 0,
        # "flex_sensor_5_max": 382
        # }

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

