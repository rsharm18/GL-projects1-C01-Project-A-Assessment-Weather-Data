from datetime import datetime
from os import device_encoding
from random import randint

from model import (
    AccessValidator,
    DailyReportModel,
    DeviceModel,
    UserDeviceAccessModel,
    UserModel,
    WeatherDataModel,
)

daily_report_model = DailyReportModel()


## userd based access validation
def execute(context_user):
    user_coll = UserModel()
    print(f"context user: {context_user}")

    print(
        f"\nDoes '{context_user}' have admin access? \n{AccessValidator.is_admin_user(context_user)}"
    )

    print(f"\nIs username based query possible for '{context_user}'?")
    user_document = user_coll.find_by_username(context_user, context_user)
    if user_document == -1:
        print(user_coll._latest_error)
    else:
        print(f"{user_document}")

    print(f"\nCan '{context_user}' add a new user?")
    access_list = [{"did": "DT004", "atype": "r"}, {"did": "DH003", "atype": "rw"}]
    # Shows a successful attempt on how to insert a user
    user_document = user_coll.insert(
        context_user, "user_4", "user_4@example.com", "default", access_list
    )
    if user_document == -1:
        print(user_coll._latest_error)
    else:
        print(f"New User added : {user_document}")

    # Shows how to initiate and search in the devices collection based on a device id
    device_coll = DeviceModel()

    device_id = "DT004"
    print(f"\nCan '{context_user}' access device {device_id}?")
    device_document = device_coll.find_by_device_id(context_user, device_id)
    if device_document == -1:
        print(device_coll.latest_error)
    else:
        print(device_document)

    device_id = "DT801"
    print(f"\nCan '{context_user}' create device {device_id} ?")
    # Shows a successful attempt on how to insert a new device
    device_document = device_coll.insert(
        context_user, device_id, "Temperature Sensor", "Temperature", "Acme"
    )
    if device_document == -1:
        print(device_coll.latest_error)
    else:
        print(device_document)

    device_id = "DT004"
    print(f"\nCan '{context_user}' read {device_id} device data?")
    device_document = device_coll.find_by_device_id(context_user, device_id)
    if device_document == -1:
        print(f"Read access not allowed to {device_id} data")
    else:
        print(device_document)

    device_id = "DH002"
    wdata_coll = WeatherDataModel()
    print(f"\nCan '{context_user}' read weather data for {device_id} device data?")
    wdata_document = wdata_coll.find_by_device_id_and_timestamp(
        context_user, device_id, datetime(2020, 12, 2, 13, 30, 0)
    )
    if wdata_document == -1:
        print(wdata_coll._latest_error)
    else:
        print(wdata_document)

    print(f"\nCan '{context_user}' add weather data for {device_id} device data?")
    wdata_document = wdata_coll.insert(
        context_user, device_id, 12, datetime(2022, 12, 4, 13, 30, 0)
    )
    if wdata_document == -1:
        print(wdata_coll.latest_error)
    else:
        print(wdata_document)

    device_id = "DT004"

    print(f"\nGenerate daily reports for {device_id} \n")
    from_date = "2020-12-05"
    to_date = "2020-12-05"
    generate_daily_reports(context_user, device_id, from_date, to_date)
    print("")
    from_date = "2020-12-03"
    generate_daily_reports(context_user, device_id, from_date, to_date)


def generate_daily_reports(context_user, device_id, from_date, to_date):
    result = daily_report_model.get_daily_report(
        context_user, device_id, from_date, to_date
    )
    if result == -1:
        print(f"{daily_report_model._latest_error}")
    return


# Shows how to initiate and search in the users collection based on a username

print("##############  ADMIN ACCESS Validation ################\n")
context_user = "admin"
execute(context_user)

print("\n############## NON ADMIN ACCESS Validation ################\n")
context_user = "user_1"
execute(context_user)
# Shows a successful attempt on how to insert a new device

# print("\n############## NON ADMIN ACCESS ERROR : START ################")
# device_document = device_coll.insert(
#     "DT201", "Temperature Sensor", "Temperature", "Acme", "user1"
# )
# if device_document == -1:
#     print(device_coll.latest_error)
# else:
#     print(device_document)

# print("############## NON ADMIN ACCESS ERROR : END ################\n")
# # Shows how to initiate and search in the weather_data collection based on a device_id and timestamp
# wdata_coll = WeatherDataModel()
# wdata_document = wdata_coll.find_by_device_id_and_timestamp(
#     context_user, "DT002", datetime(2020, 12, 2, 13, 30, 0)
# )
# if wdata_document:
#     print(wdata_document)

# # Shows a failed attempt on how to insert a new data point
# wdata_document = wdata_coll.insert(
#     context_user, "DT002", 12, datetime(2020, 12, 2, 13, 30, 0)
# )
# if wdata_document == -1:
#     print(wdata_coll.latest_error)
# else:
#     print(wdata_document)

# print(" ############# Printing the device access location ##################")
# user_device_access = UserDeviceAccessModel()
# uda_document = user_device_access.find_device_access_list_by_username("user_1")

# print(uda_document)

# print("check user device acess")
# username = input("Enter username: ")
# device_id = input("Enter device id: ")
# print(f"\nCan {username} access device {device_id}?")

# uda_document = user_device_access.check_device_access_for_username(username, device_id)
# if not uda_document:
#     print(f" Read access not allowed to {device_id} for user {username}")
# else:
#     res = [
#         access
#         for access in uda_document["device_access_list"]
#         if access["did"] == device_id
#     ][0]["atype"]
#     print(f"{username} has the '{res}' access to {device_id}")

# print("\n############################## END #################### \n")
