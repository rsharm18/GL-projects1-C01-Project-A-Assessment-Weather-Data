# Imports Database class from the project to provide basic functionality for database access
from database import Database
# Imports ObjectId to convert to the correct format before querying in the db
from bson.objectid import ObjectId

class AccessValidator:

    @staticmethod
    def isAccessAllowed(context_user_name):
        user_coll = UserModel()
        user = user_coll.find_by_username(context_user_name)
        if user and user['role']=='admin':
            return True
        else:
            return False
       

# User document contains username (String), email (String), and role (String) fields
class UserModel:
    USER_COLLECTION = 'users'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since username should be unique in users collection, this provides a way to fetch the user document based on the username
    def find_by_username(self, username):
        key = {'username': username}
        return self.__find(key)
    
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id):
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        user_document = self._db.get_single_data(UserModel.USER_COLLECTION, key)
        return user_document
    
    # This first checks if a user already exists with that username. If it does, it populates latest_error and returns -1
    # If a user doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, context_user, new_user_name, email, role):
        self._latest_error = ''
        if not AccessValidator.isAccessAllowed(context_user):
            self._latest_error=f'user {context_user} does not the access to perform the operation'
            return -1
        user_document = self.find_by_username(new_user_name)
        if (user_document):
            self._latest_error = f'Username {new_user_name} already exists'
            return -1
        
        user_data = {'username': new_user_name, 'email': email, 'role': role}
        user_obj_id = self._db.insert_single_data(UserModel.USER_COLLECTION, user_data)
        return self.find_by_object_id(user_obj_id)


# Device document contains device_id (String), desc (String), type (String - temperature/humidity) and manufacturer (String) fields
class DeviceModel:
    DEVICE_COLLECTION = 'devices'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since device id should be unique in devices collection, this provides a way to fetch the device document based on the device id
    def find_by_device_id(self, device_id, context_user_name):
        # print("find_by_device_id - user access allowed ? ", self.access_validator.isAccessAllowed(user_name))
        key = {'device_id': device_id}
        return self.__find(key,context_user_name)
    
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id, context_user_name):
        # print("find_by_object_id - user access allowed ? ", self.access_validator.isAccessAllowed(user_name))
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key,context_user_name)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key, context_user_name):
        if not AccessValidator.isAccessAllowed(context_user_name):
            self._latest_error=f'user {context_user_name} does not the access to perform the operation'
            return -1
        # print("find - user access allowed ? ", self.access_validator.isAccessAllowed(user_name))
        device_document = self._db.get_single_data(DeviceModel.DEVICE_COLLECTION, key)
        return device_document
    
    # This first checks if a device already exists with that device id. If it does, it populates latest_error and returns -1
    # If a device doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, desc, type, manufacturer, context_user_name):
        # print("insert - user access allowed ? ", self.access_validator.isAccessAllowed(user_name))
        self._latest_error = ''
        if not AccessValidator.isAccessAllowed(context_user_name):
            self._latest_error=f'user {context_user_name} does not have the access to perform the operation'
            return -1

        device_document = self.find_by_device_id(device_id,context_user_name)
        if (device_document):
            self._latest_error = f'Device id {device_id} already exists'
            return -1
        
        device_data = {'device_id': device_id, 'desc': desc, 'type': type, 'manufacturer': manufacturer}
        device_obj_id = self._db.insert_single_data(DeviceModel.DEVICE_COLLECTION, device_data)
        return self.find_by_object_id(device_obj_id,context_user_name)


# Weather data document contains device_id (String), value (Integer), and timestamp (Date) fields
class WeatherDataModel:
    WEATHER_DATA_COLLECTION = 'weather_data'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since device id and timestamp should be unique in weather_data collection, this provides a way to fetch the data document based on the device id and timestamp
    def find_by_device_id_and_timestamp(self, device_id, timestamp, context_user_name):
        # print("weather - find_by_device_id_and_timestamp - user access allowed ? ", self.access_validator.isAccessAllowed(user_name))
        key = {'device_id': device_id, 'timestamp': timestamp}
        return self.__find(key,context_user_name)
    
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id, context_user_name):
        # print("weather - find_by_object_id - user access allowed ? ", self.access_validator.isAccessAllowed(user_name))
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key, context_user_name)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key, context_user_name):
        if not AccessValidator.isAccessAllowed(context_user_name):
            self._latest_error=f'user {context_user_name} does not the access to perform the operation'
            return -1
        wdata_document = self._db.get_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, key)
        return wdata_document
    
    # This first checks if a data item already exists at a particular timestamp for a device id. If it does, it populates latest_error and returns -1.
    # If it doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, value, timestamp, context_user_name):
        self._latest_error = ''
        if not AccessValidator.isAccessAllowed(context_user_name):
            self._latest_error=f'user {context_user_name} does not the access to perform the operation'
            return -1
        wdata_document = self.find_by_device_id_and_timestamp(device_id, timestamp, context_user_name)
        if (wdata_document):
            self._latest_error = f'Data for timestamp {timestamp} for device id {device_id} already exists'
            return -1
        
        weather_data = {'device_id': device_id, 'value': value, 'timestamp': timestamp}
        wdata_obj_id = self._db.insert_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, weather_data)
        return self.find_by_object_id(wdata_obj_id)

# User Device access document contains username (String), email (String), role (String), accessList fields
class UserDeviceAcessModel:
    USER_DEVICE_ACCESS_COLLECTION = 'users_device_access'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.userModel = UserModel()
        # self.device_access_list = []
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # @property
    # def device_access_list(self):
    #     return self._device_access_list

    # Since username should be unique in users collection, this provides a way to fetch the user document based on the username
    def find_device_access_list_by_username(self, username):
        key = {'username': username}
        return self.__find(key)
    
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id):
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)
    
    def check_device_access_for_username(self, username,device_id):
        key= {'username':username,'device_access_list.did':device_id}
        return self.__find(key)

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        user_document = self._db.get_single_data(UserDeviceAcessModel.USER_DEVICE_ACCESS_COLLECTION, key)
        return user_document
    
    # This first checks if a user exists with that username. If it does not, it populates latest_error and returns -1
    # If a user already exists, it'll insert a new/update the existing document and return the same to the caller
    def insert(self, context_user, user_name, access_list):
        self._latest_error = ''
        if not AccessValidator.isAccessAllowed(context_user):
            self._latest_error=f'user {context_user} does not the access to perform the operation'
            return -1
        user_document = self.userModel.find_by_username(user_name)
        if not user_document:
            self._latest_error = f'Username {user_name} does not exist'
            return -1
# User Device access document contains username (String), email (String), role (String), accessList fields
        # 
        user_access = {'username': user_document.username, 'email': user_document.email, 'role': user_document.role,'device_access_list':access_list}
        user_obj_id = self._db.insert_single_data(UserDeviceAcessModel.USER_DEVICE_ACCESS_COLLECTION, user_access)
        return self.find_by_object_id(user_obj_id)