import pymongo
from pymongo.errors import PyMongoError

import log
from consts import *

logger = log.setup_custom_logger('DBHandler')
my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_client["Carpool"]
drivers_collection = my_db["Drivers"]
passengers_collection = my_db["Passengers"]


def is_user_exist_in_db(type_of_user, user_id):
    logger.info('Check if the %s with phone-number=%s already exist in DB (%s collection)',
                type_of_user, user_id, type_of_user)
    relevant_collection = (drivers_collection, passengers_collection)[type_of_user == passenger_type]

    return not relevant_collection.find_one({
        phone_number: user_id
    }) is None


def create_new_user(type_of_user, user_data):
    logger.info('Trying to create new %s in DB', type_of_user)
    relevant_collection = (drivers_collection, passengers_collection)[type_of_user == passenger_type]

    try:
        if is_user_exist_in_db(type_of_user, user_data.get(phone_number)):
            logger.warning('The %s already exist in DB', type_of_user)
            logger.error("user didn't created in DB")

            return "user already exist in DB"
        else:
            logger.info("%s doesn't exist in DB", type_of_user)
            logger.info('Trying to insert the %s to DB', type_of_user)

            relevant_collection.insert_one(user_data)

            logger.info('user creation completed successfully')

            return 'user creation completed successfully'
    except PyMongoError as err:
        logger.error(str(err))
        logger.warning('User does not created')

        return 'User does not created'


def is_data_changed(old_data, new_data):
    return not old_data == new_data


def update_user(type_of_user, user_new_data):
    logger.info('Trying to update user with phone_number=%s data in DB (%s collection)',
                user_new_data.get(phone_number), type_of_user)
    relevant_collection = (drivers_collection, passengers_collection)[type_of_user == passenger_type]

    try:
        if not is_user_exist_in_db(type_of_user, user_new_data.get(phone_number)):
            logger.error('User does not exist in DB (%s collection)', type_of_user)

            return 'User does not exist in DB (%s collection)', type_of_user
        else:
            logger.info('User founded in DB')
            logger.info('Trying to update user data')

            old_user_data = relevant_collection.find_one({phone_number: user_new_data.get(phone_number)}, {ID: 0})

            logger.info('Making sure the user data needs to be updated')
            if is_data_changed(old_user_data, user_new_data):
                logger.info('User data has changed, trying to update in DB')
                relevant_collection.update_one(old_user_data, {"$set": user_new_data})
                logger.info('Update user completed successfully')

                return 'Update user completed successfully'
            else:
                logger.info('User data has no changes, not updating the DB')

                return 'User data has no changes, not updating the DB'
    except PyMongoError as err:
        logger.error(str(err))
        logger.warning('User does not updated')

        return 'User does not updated'


def delete_user(type_of_user, user_id):
    logger.info('Trying to delete user with phone_number=%s from DB (%s collection)', user_id, type_of_user)
    relevant_collection = (drivers_collection, passengers_collection)[type_of_user == passenger_type]

    try:
        if not is_user_exist_in_db(type_of_user, user_id):
            logger.error('User with phone-number=%s does not exist in DB (%s collection)', user_id, type_of_user)

            return 'User does not exist in DB'
        else:
            logger.info('User founded in DB')
            logger.info('Trying to delete user')

            relevant_collection.delete_one({phone_number: user_id})

            logger.info('User deleted successfully')

            return 'User deleted successfully'
    except PyMongoError as err:
        logger.error(str(err))
        logger.warning('User does not deleted')

        return 'User does not deleted'
