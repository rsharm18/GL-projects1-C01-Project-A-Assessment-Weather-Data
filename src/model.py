# Imports Database class from the project to provide basic functionality for database access
from datetime import datetime

# Imports ObjectId to convert to the correct format before querying in the db
from bson.objectid import ObjectId
from pymongo import results

from database import Database


class AccessValidator:
    @staticmethod
    def allow_device_read(context_user, device_id):

        if AccessValidator.is_admin_user(context_user):
            return True

        user_device_access_model = UserDeviceAccessModel()
        user_device_access_collection = (
            user_device_access_model.check_device_access_for_username_device_id(
                context_user, device_id
            )
        )

        if user_device_access_collection:
            return True

        return False

    @staticmethod
    def is_admin_user(context_user):
        user_coll = UserModel()
        user = user_coll.find_by_username(context_user, context_user, True)
        if user and user["role"] == "admin":
            return True
        else:
            return False

    @staticmethod
    def allow_create(context_user):
        return AccessValidator.is_admin_user(context_user)

    @staticmethod
    def allow_device_update(context_user, device_id):
        if AccessValidator.is_admin_user(context_user):
            return True

        else:
            user_device_access_model = UserDeviceAccessModel()
            result = (
                user_device_access_model.check_device_access_for_username_device_id(
                    context_user, device_id
                )
            )
            if result and result["device_access_list"]:
                access_list = filter(
                    lambda access_data: access_data["atype"] == "rw"
                    and access_data["did"] == device_id,
                    result["device_access_list"],
                )
                # print(f" device access list {list(access_list)}")
                return len(list(access_list)) > 0

        return False


# User document contains username (String), email (String), and role (String) fields
class UserModel:
    USER_COLLECTION = "users"

    def __init__(self):
        self._db = Database()
        self._latest_error = ""
        self._user_device_access_model = UserDeviceAccessModel()
        self._alist = []

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Since username should be unique in users collection, this provides a way to fetch the user document based on the username
    def find_by_username(self, context_user, username, skip_admin_check=False):
        if not skip_admin_check and not AccessValidator.is_admin_user(context_user):
            self._latest_error = "Query failed, Admin access required!"
            return -1

        key = {"username": username}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id
    def find_by_object_id(self, context_user, obj_id):
        if not AccessValidator.is_admin_user(context_user):
            self._latest_error = "Query failed, Admin access required!"
            return -1

        key = {"_id": ObjectId(obj_id)}
        return self.__find(key)

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        user_document = self._db.get_single_data(UserModel.USER_COLLECTION, key)

        if user_document:
            ## append user access list to user data
            user_device_access_coll = (
                self._user_device_access_model.find_device_access_list_by_username(
                    user_document["username"]
                )
            )
            user_document["alist"] = (
                user_device_access_coll["device_access_list"]
                if user_device_access_coll
                else []
            )
        return user_document

    # This first checks if a user already exists with that username. If it does, it populates latest_error and returns -1
    # If a user doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, context_user, new_user_name, email, role, alist=[]):
        self._latest_error = ""
        if not AccessValidator.allow_create(context_user):
            self._latest_error = f"Insert failed, Admin access required!"
            return -1

        user_document = self.find_by_username(context_user, new_user_name)
        if user_document:
            self._latest_error = f"Username {new_user_name} already exists"
            return -1

        user_data = {"username": new_user_name, "email": email, "role": role}
        user_obj_id = self._db.insert_single_data(UserModel.USER_COLLECTION, user_data)

        user_document = self.find_by_object_id(context_user, user_obj_id)

        # add the new user to device access list
        self._user_device_access_model.insert(
            context_user, user_document["username"], alist
        )
        return user_document


# Device document contains device_id (String), desc (String), type (String - temperature/humidity) and manufacturer (String) fields
class DeviceModel:
    DEVICE_COLLECTION = "devices"

    def __init__(self):
        self._db = Database()
        self._latest_error = ""

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Since device id should be unique in devices collection, this provides a way to fetch the device document based on the device id
    def find_by_device_id(self, context_user, device_id):

        if not AccessValidator.allow_device_read(context_user, device_id):
            self._latest_error = (
                f"{context_user} user does not have read access to device {device_id}"
            )
            return -1

        key = {"device_id": device_id}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id
    def find_by_object_id(self, context_user, obj_id):

        key = {"_id": ObjectId(obj_id)}

        device_collection = self.__find(key)

        if device_collection and AccessValidator.allow_device_read(
            context_user, device_collection["device_id"]
        ):
            return device_collection

        self._latest_error = f"{context_user} does not have the read access to {obj_id}"
        return -1

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        device_document = self._db.get_single_data(DeviceModel.DEVICE_COLLECTION, key)
        return device_document

    # This first checks if a device already exists with that device id. If it does, it populates latest_error and returns -1
    # If a device doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, context_user, device_id, desc, type, manufacturer):
        # print("insert - user access allowed ? ", self.access_validator.allow_device_read(user_name))
        self._latest_error = ""
        if not AccessValidator.allow_create(context_user):
            self._latest_error = f"Insert failed, Admin access required!"
            return -1

        device_document = self.find_by_device_id(context_user, device_id)
        if device_document and device_document != -1:
            self._latest_error = f"Device id {device_id} already exists"
            return device_document

        device_data = {
            "device_id": device_id,
            "desc": desc,
            "type": type,
            "manufacturer": manufacturer,
        }
        device_obj_id = self._db.insert_single_data(
            DeviceModel.DEVICE_COLLECTION, device_data
        )
        return self.find_by_object_id(context_user, device_obj_id)


# Weather data document contains device_id (String), value (Integer), and timestamp (Date) fields
class WeatherDataModel:
    WEATHER_DATA_COLLECTION = "weather_data"

    def __init__(self):
        self._db = Database()
        self._latest_error = ""

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Since device id and timestamp should be unique in weather_data collection, this provides a way to fetch the data document based on the device id and timestamp
    def find_by_device_id_and_timestamp(self, context_user, device_id, timestamp):

        if not AccessValidator.allow_device_read(context_user, device_id):
            self._latest_error = f"{context_user} does not have the Read (r) access to the device {device_id}"
            return -1

        key = {"device_id": device_id, "timestamp": timestamp}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id
    def find_by_object_id(self, context_user, obj_id):
        # print("weather - find_by_object_id - user access allowed ? ", self.access_validator.allow_device_read(user_name))
        key = {"_id": ObjectId(obj_id)}
        weather_data_collection = self.__find(key)

        if weather_data_collection and AccessValidator.allow_device_read(
            context_user, weather_data_collection["device_id"]
        ):
            return weather_data_collection

        self._latest_error = f"{context_user} does not have the read access to {obj_id}"
        return -1

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        wdata_document = self._db.get_single_data(
            WeatherDataModel.WEATHER_DATA_COLLECTION, key
        )
        return wdata_document

    # This first checks if a data item already exists at a particular timestamp for a device id. If it does, it populates latest_error and returns -1.
    # If it doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, context_user, device_id, value, timestamp):
        self._latest_error = ""

        if not AccessValidator.allow_device_update(context_user, device_id):
            self._latest_error = f"{context_user} does not have the create (rw) access"
            return -1

        wdata_document = self.find_by_device_id_and_timestamp(
            context_user, device_id, timestamp
        )

        if wdata_document:
            self._latest_error = f"Data for timestamp {timestamp} for device id {device_id} already exists"
            return -1

        weather_data = {"device_id": device_id, "value": value, "timestamp": timestamp}
        wdata_obj_id = self._db.insert_single_data(
            WeatherDataModel.WEATHER_DATA_COLLECTION, weather_data
        )
        return self.find_by_object_id(context_user, wdata_obj_id)


# User Device access document contains username (String), email (String), role (String), accessList fields
class UserDeviceAccessModel:
    USER_DEVICE_ACCESS_COLLECTION = "users_device_access"

    def __init__(self):
        self._db = Database()
        self._latest_error = ""

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # @property
    # def device_access_list(self):
    #     return self._device_access_list

    # Since username should be unique in users collection, this provides a way to fetch the user document based on the username
    def find_device_access_list_by_username(self, username):
        key = {"username": username}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id
    def find_by_object_id(self, obj_id):
        key = {"_id": ObjectId(obj_id)}
        return self.__find(key)

    def check_device_access_for_username_device_id(self, context_user, device_id):
        # if AccessValidator.is_admin_user(context_user):
        #     return True
        key = {"username": context_user, "device_access_list.did": device_id}
        return self.__find(key)

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        user_device_access_document = self._db.get_single_data(
            UserDeviceAccessModel.USER_DEVICE_ACCESS_COLLECTION, key
        )
        return user_device_access_document

    # This first checks if a user exists with that username. If it does not, it populates latest_error and returns -1
    # If a user already exists, it'll insert a new/update the existing document and return the same to the caller
    def insert(self, context_user, user_name, access_list):
        self._latest_error = ""
        if not AccessValidator.allow_create(context_user):
            self._latest_error = f"user {context_user} does not have the create access"
            return -1

        userModel = UserModel()
        user_document = userModel.find_by_username(context_user, user_name)
        if not user_document:
            self._latest_error = f"Username {user_name} does not exist"
            return -1

        # User Device access document contains username (String), email (String), role (String), accessList fields
        user_access = {
            "username": user_document["username"],
            "email": user_document["email"],
            "role": user_document["role"],
            "device_access_list": access_list,
        }
        user_obj_id = self._db.insert_single_data(
            UserDeviceAccessModel.USER_DEVICE_ACCESS_COLLECTION, user_access
        )
        return self.find_by_object_id(user_obj_id)


class DailyReportModel:
    DAILY_REPORTS_COLLECTION = "daily_reports"

    def __init__(self):
        self._db = Database()
        self._latest_error = ""

    def insert(self, context_user, device_id, average, minimum, maximum, timestamp):
        if not AccessValidator.allow_create(context_user):
            self._latest_error = f"user {context_user} does not have the create access for Daily Reports data"
            return -1

        new_daily_report_document = {
            "device_id": device_id,
            "avg_value": average,
            "min_value": minimum,
            "max_value": maximum,
            "date": timestamp,
        }
        daily_report_document = self._db.insert_single_data(
            DailyReportModel.DAILY_REPORTS_COLLECTION, new_daily_report_document
        )
        return daily_report_document

    def get_daily_report(self, context_user, device_id, from_date, to_date):

        from_date = datetime.fromisoformat(from_date)
        to_date = datetime.fromisoformat(to_date)

        if from_date > to_date:
            self._latest_error = "Invalid Date Range. From Date cannot be after To date"
            return -1

        if not AccessValidator.allow_device_read(context_user, device_id):
            self._latest_error = (
                f"{context_user} does not have the read access to device {device_id}"
            )
            return -1

        query = [
            {
                "$match": {
                    "date": {"$lte": to_date, "$gte": from_date},
                    "device_id": device_id,
                }
            }
        ]
        result_cursor = self._db.aggregate_data(self.DAILY_REPORTS_COLLECTION, query)
        result = []
        num_of_days = to_date - from_date
        print(
            f"Date Range : {from_date} - {to_date} : Get daily report for {'multiple days' if num_of_days.days > 0 else 'one day'}"
        )
        for doc in result_cursor:
            result.append(doc)

        print(result)
        return result
