import json
import random

# Imports datetime class to create timestamp for weather data storage
from datetime import datetime
from itertools import groupby

# Imports MongoClient for base level access to the local MongoDB
from pymongo import MongoClient

# Database host ip and port information
HOST = "127.0.0.1"
PORT = "27017"

RELATIVE_CONFIG_PATH = "../config/"

DB_NAME = "weather_db"
USER_COLLECTION = "users"
DEVICE_COLLECTION = "devices"
WEATHER_DATA_COLLECTION = "weather_data"
USER_DEVICE_ACCESS_COLLECTION = "users_device_access"
DAILY_REPORTS = "daily_reports"

# This will initiate connection to the mongodb
db_handle = MongoClient(f"mongodb://{HOST}:{PORT}")

# We drop the existing database including all the collections and data
db_handle.drop_database(DB_NAME)

# We recreate the database with the same name
weather_dbh = db_handle[DB_NAME]


# user data import
# User document contains username (String), email (String), and role (String) fields
# Reads users.csv one line at a time, splits them into the data fields and inserts
with open(RELATIVE_CONFIG_PATH + USER_COLLECTION + ".csv", "r") as user_fh:
    for user_row in user_fh:
        user_row = user_row.rstrip()
        # print(user_row.split(','))
        if user_row:
            (username, email, role) = user_row.split(",", maxsplit=3)

        user_data = {"username": username, "email": email, "role": role}

        # print("\nuser_data ",user_data)
        # This creates and return a pointer to the users collection
        user_collection = weather_dbh[USER_COLLECTION]

        # This inserts the data item as a document in the user collection
        user_collection.insert_one(user_data)

# device data import
# Device document contains device_id (String), desc (String), type (String - temperature/humidity) and manufacturer (String) fields
# Reads devices.csv one line at a time, splits them into the data fields and inserts
with open(RELATIVE_CONFIG_PATH + DEVICE_COLLECTION + ".csv", "r") as device_fh:
    for device_row in device_fh:
        device_row = device_row.rstrip()
        if device_row:
            (device_id, desc, type, manufacturer) = device_row.split(",")
        device_data = {
            "device_id": device_id,
            "desc": desc,
            "type": type,
            "manufacturer": manufacturer,
        }

        # This creates and return a pointer to the devices collection
        device_collection = weather_dbh[DEVICE_COLLECTION]

        # This inserts the data item as a document in the devices collection
        device_collection.insert_one(device_data)

# weather data generation
# Weather data document contains device_id (String), value (Integer), and timestamp (Date) fields
# Reads devices.csv one line at a time to get device id and type. It then loops for five days (2020-12-01 to 2020-12-05
# For each device and day, it creates random values for each hour (at the 30 minute mark) and stores the data
with open(RELATIVE_CONFIG_PATH + DEVICE_COLLECTION + ".csv", "r") as device_fh:
    for device_row in device_fh:
        device_row = device_row.rstrip()
        if device_row:
            # _ can be used to ignore values that are not needed
            (device_id, _, type, _) = device_row.split(",")
        for day in range(1, 6):
            for hour in range(0, 24):
                timestamp = datetime(2020, 12, day, hour, 30, 0)
                # Generates random data value in appropriate range as per the type of sensor (normal bell-curve distribution)
                if type.lower() == "temperature":
                    value = int(random.normalvariate(24, 2.2))
                elif type.lower() == "humidity":
                    value = int(random.normalvariate(45, 3))
                weather_data = {
                    "device_id": device_id,
                    "value": value,
                    "timestamp": timestamp,
                }

                # This creates and return a pointer to the weather_data collection
                weather_data_collection = weather_dbh[WEATHER_DATA_COLLECTION]

                # This inserts the data item as a document in the weather_data collection
                weather_data_collection.insert_one(weather_data)

# users_device_access data import
# User document contains username (String), email (String), and role (String) fields
# Reads users_device_access.csv one line at a time, splits them into the data fields and inserts
with open(
    RELATIVE_CONFIG_PATH + USER_DEVICE_ACCESS_COLLECTION + ".csv", "r"
) as user_fh:
    for user_row in user_fh:
        user_row = user_row.rstrip()
        if user_row:
            (username, email, role, alist) = user_row.split(",", maxsplit=3)

        user_data = {
            "username": username,
            "email": email,
            "role": role,
            "device_access_list": json.loads(alist),
        }

        # This creates and return a pointer to the users collection
        user_collection = weather_dbh[USER_DEVICE_ACCESS_COLLECTION]

        # This inserts the data item as a document in the user collection
        user_collection.insert_one(user_data)

## Read from weather collection and calculate the average, minimum and maximum and insert data into daily_reports collection
weather_data_collection = weather_dbh[WEATHER_DATA_COLLECTION]
pipeline = [
    {
        "$group": {
            "_id": {
                "deviceId": "$device_id",
                "timestamp": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$timestamp",
                    }
                },
            },
            "averageValue": {"$avg": "$value"},
            "minimumValue": {"$min": "$value"},
            "maximumValue": {"$min": "$value"},
        }
    },
    {
        "$project": {
            "_id": 0,
            "device_id": "$_id.deviceId",
            "date": {
                "$dateFromString": {
                    "dateString": "$_id.timestamp",
                    "format": "%Y-%m-%d",
                }
            },
            "avg_value": "$averageValue",
            "min_value": "$minimumValue",
            "max_value": "$maximumValue",
        }
    },
]

## Bulk aggregation in daily_reports collection
result = weather_data_collection.aggregate(pipeline)
daily_report_collection = weather_dbh[DAILY_REPORTS]
for doc in result:
    daily_report_collection.insert_one(doc)
