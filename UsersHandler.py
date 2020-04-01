import DBHandler
import log
from consts import *
from requests import RequestException
from datetime import datetime


logger = log.setup_custom_logger()
firebase_db = DBHandler.get_firebase_db_ref()


def get_all_users_from_db():
    logger.info('Trying to get all users from DB')
    return firebase_db.child(users_collection).get().items()


def get_user_from_db(user_id):
    logger.info('Check if user with phone-number=%s exists in DB', user_id)
    all_users = get_all_users_from_db()

    for user in all_users:
        if user[values_position].get(phone_number) == user_id:
            logger.info('User exists in DB')
            return user

    return None


def create_new_user(new_user_data):
    logger.info('Trying to create new user in DB')

    try:
        if get_user_from_db(new_user_data.get(phone_number)) is not None:
            logger.error("New user wasn't created")

            return "User already exists in DB"
        else:
            logger.info("User doesn't exists in DB")
            logger.info('Trying to insert the user to DB')

            firebase_db.child(users_collection).push(new_user_data)

            logger.info('User creation completed successfully')

            return 'User creation completed successfully'
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User wasn't created")

        return "User wasn't created"


def update_user(user_updated_data):
    logger.info('Trying to update user with phone_number=%s in DB', user_updated_data.get(phone_number))

    try:
        logger.info('Trying to get old user from DB')
        user_old_data = get_user_from_db(user_updated_data.get(phone_number))

        if user_old_data is not None:
            logger.info('Trying to update user data')
            firebase_db.child(users_collection).child(user_old_data[key_position]).set(user_updated_data)
            logger.info('Update user completed successfully')

            return 'Update user completed successfully'
        else:
            logger.error("User doesn't exists in DB")

            return "User doesn't exists in DB"
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User doesn't updated")
        return 'User does not updated'


def delete_user(user_id):
    logger.info('Trying to delete user with phone_number=%s from DB', user_id)

    try:
        logger.info('Trying to get user from DB')
        user_to_delete = get_user_from_db(user_id)
        if user_to_delete is not None:
            logger.info('Trying to delete user')
            firebase_db.child(users_collection).child(user_to_delete[key_position]).delete()
            logger.info('User deleted successfully')

            return 'User deleted successfully'
        else:
            logger.error("User doesn't exists in DB")

            return "User doesn't exists in DB"
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User wasn't deleted")

        return "User wasn't deleted"


def restore_user(user_id):
    logger.info('Trying to restore user from DB')
    user_to_restore = get_user_from_db(user_id)

    if user_to_restore is not None:
        logger.info('Restoring user completed successfully')

        return user_to_restore
    else:
        logger.error("User doesn't exists in DB")

        return "User doesn't exists in DB"