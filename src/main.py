from datetime import datetime
from random import randint

from model import (
    AccessValidator,
    DailyReportModel,
    DeviceModel,
    UserModel,
    WeatherDataModel,
)

daily_report_model = DailyReportModel()


def execute_with_user_prompt():
    user_coll = UserModel()

    context_user = input("\nEnter User Name : ")
    print(f"context user: {context_user}")
    print("\n########### VALIDATE USER MODEL ACCESS ##################\n")
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
    new_user_name = input("\nEnter New User Name : ")
    user_document = user_coll.insert(
        context_user,
        new_user_name,
        f"{new_user_name}@example.com",
        "default",
        access_list,
    )
    if user_document == -1:
        print(user_coll._latest_error)
    else:
        print(f"New User added : {user_document}")

    print("\n########### VALIDATE DEVICE MODEL ACCESS ##################\n")

    # Shows how to initiate and search in the devices collection based on a device id
    device_coll = DeviceModel()

    device_id = input("\nEnter existing device Id : ")
    print(f"\nCan '{context_user}' access device {device_id}?")
    device_document = device_coll.find_by_device_id(context_user, device_id)
    if device_document == -1:
        print(device_coll.latest_error)
    else:
        print(device_document)

    new_device_id = input("\nCREATE NEW DEVICE : Enter new device Id : ")
    print(f"\nCan '{context_user}' create device {device_id} ?")

    # Shows a successful attempt on how to insert a new device
    device_document = device_coll.insert(
        context_user, new_device_id, "Temperature Sensor", "Temperature", "Acme"
    )
    if device_document == -1:
        print(device_coll.latest_error)
    else:
        print(device_document)

    device_id = input("\nEnter existing device Id to Check Read access: ")
    print(f"\nCan '{context_user}' read {device_id} device data?")
    device_document = device_coll.find_by_device_id(context_user, device_id)
    if device_document == -1:
        print(f"Read access not allowed to {device_id} data")
    else:
        print(device_document)

    print("\n########### VALIDATE WEATHER MODEL ACCESS ##################\n")

    device_id = input("\nEnter existing Weatherdevice Id ")
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
        context_user, device_id, 12, datetime(2022, 12, randint(1, 20), 13, 30, 0)
    )
    if wdata_document == -1:
        print(wdata_coll.latest_error)
    else:
        print(wdata_document)

    print("\n########### VALIDATE DAILY REPORT GENERATION ##################\n")

    device_id = input("\nEnter existing device Id for Daily Report for one day ")
    from_date = input("\nEnter From Date e.g. 2020-12-05 ")
    to_date = input("\nEnter To Date e.g. 2020-12-05 ")

    print(f"\nGenerate daily reports for {device_id} \n")

    generate_daily_reports(context_user, device_id, from_date, to_date)
    print(f"\n Daily Report for multiple days for {device_id} \n")
    from_date = input("\nEnter From Date e.g. 2020-12-03 ")
    to_date = input("\nEnter To Date (e.g. 2020-12-05 ")
    generate_daily_reports(context_user, device_id, from_date, to_date)


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
        context_user, device_id, 12, datetime(2022, 12, randint(1, 20), 13, 30, 0)
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


print("\n############################## START #################### \n")

mode = input(
    "Enter \n A for auto execute \n I for interactive mode \n AI for both \n Q to Quit \n "
)

while mode != "Q":
    mode = mode.upper()
    if mode == "A" or mode == "AI":
        print("##############  ADMIN ACCESS Validation ################\n")
        context_user = "admin"
        execute(context_user)
        print("\n############## NON ADMIN ACCESS Validation ################\n")
        context_user = "user_1"
        execute(context_user)

    if mode == "I" or mode == "AI":
        print("\n ############ RUNNING IN INTERACTIVE MODE ###############\n\n")
        execute_with_user_prompt()

    if mode == "Q":
        print("\n\nBye!")
    else:
        mode = input(
            "\nEnter \n A for auto execute \n I for interactive mode \n AI for both \n Q to Quit \n "
        )


print("\n############################## END #################### \n")
