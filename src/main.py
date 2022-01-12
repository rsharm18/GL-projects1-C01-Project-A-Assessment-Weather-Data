from model import UserDeviceAcessModel, UserModel, DeviceModel, WeatherDataModel
from datetime import datetime


# Shows how to initiate and search in the users collection based on a username
user_coll = UserModel()
user_document = user_coll.find_by_username('admin')
if (user_document):
    print(user_document)

# Shows a successful attempt on how to insert a user
user_document = user_coll.insert('admin','test_3', 'test_3@example.com', 'default')
if (user_document == -1):
    print(user_coll.latest_error)
else:
    print(user_document)

# Shows how to initiate and search in the devices collection based on a device id
device_coll = DeviceModel()
device_document = device_coll.find_by_device_id('DT002','admin')
if (device_document):
    print(device_document)

# Shows a successful attempt on how to insert a new device
device_document = device_coll.insert('DT201', 'Temperature Sensor', 'Temperature', 'Acme','admin')
if (device_document == -1):
    print(device_coll.latest_error)
else:
    print(device_document)


device_document = device_coll.find_by_device_id('DT002','admin')
if (device_document):
    print(device_document)

# Shows a successful attempt on how to insert a new device

print("\n ############## NON ADMIN ACCESS ERROR : START ################")
device_document = device_coll.insert('DT201', 'Temperature Sensor', 'Temperature', 'Acme','user1')
if (device_document == -1):
    print(device_coll.latest_error)
else:
    print(device_document)

print("############## NON ADMIN ACCESS ERROR : END ################\n\n")
# Shows how to initiate and search in the weather_data collection based on a device_id and timestamp
wdata_coll = WeatherDataModel()
wdata_document = wdata_coll.find_by_device_id_and_timestamp('DT002', datetime(2020, 12, 2, 13, 30, 0),'admin')
if (wdata_document):
    print(wdata_document)

# Shows a failed attempt on how to insert a new data point
wdata_document = wdata_coll.insert('DT002', 12, datetime(2020, 12, 2, 13, 30, 0),'admin')
if (wdata_document == -1):
    print(wdata_coll.latest_error)
else:
    print(wdata_document)

print(" ############# Printing the device access location ##################")
user_device_access = UserDeviceAcessModel()
uda_document = user_device_access.find_device_access_list_by_username('user_1')

print(uda_document)

print('check user device acess')
username = input('Enter username: ')
device_id=input('Enter device id: ')
print(f'\n Can {username} access device {device_id}?')

uda_document = user_device_access.check_device_access_for_username(username,device_id)
if (not uda_document):
    print(f' Read access not allowed to {device_id} for user {username}')
else:
    res = [access for access in uda_document['device_access_list'] if access['did']==device_id][0]['atype']
    print(f' {username} has the \'{res}\' access to {device_id}')

print('\n\n############################## END #################### \n\n')