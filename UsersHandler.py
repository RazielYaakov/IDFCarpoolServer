from requests import RequestException

import DBHandler
import log
from consts import *

logger = log.setup_custom_logger()
firebase_db = DBHandler.get_firebase_db_ref()


def get_all_users_from_db():
    logger.info('Trying to get all users from DB')
    all_users = firebase_db.child(users_collection).get()

    if all_users is not None:
        return all_users.items()

    return None


def get_user_from_db(user_id):
    logger.info('Check if user with phoneNumber=%s exists in DB', user_id)
    all_users = get_all_users_from_db()

    if all_users is not None:
        for user in all_users:
            if user[values_position].get(phone_number) == user_id:
                logger.info('User exists in DB')
                return user

    return None


def login(user_data):
    logger.info('User with phoneNumber=%s trying to login', user_data.get(phone_number))
    logger.info('Checking user')

    try:
        if get_user_from_db(user_data.get(phone_number)) is not None:
            logger.info("Returning user's login succeeded")

            return success
        else:
            logger.info("User doesn't exists in DB")
            logger.info('Trying to insert new user to DB')

            firebase_db.child(users_collection).push(user_data)

            logger.info('User creation completed successfully')

            return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User login failed")

        return failure


def update_user(user_updated_data):
    logger.info('Trying to update user with phoneNumber=%s in DB', user_updated_data.get(phone_number))

    try:
        logger.info('Trying to get user from DB')
        user_old_data = get_user_from_db(user_updated_data.get(phone_number))

        if user_old_data is not None:
            logger.info('Trying to update user data')
            firebase_db.child(users_collection).child(user_old_data[key_position]).set(user_updated_data)
            logger.info('Update user completed successfully')

            return success
        else:
            logger.error("User doesn't exists in DB, returning %s", failure)

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User doesn't updated")

        return failure


def delete_user(user_id):
    logger.info('Trying to delete user with phoneNumber=%s from DB', user_id)

    try:
        logger.info('Trying to get user from DB')
        user_to_delete = get_user_from_db(user_id)
        if user_to_delete is not None:
            logger.info('Trying to delete user')
            firebase_db.child(users_collection).child(user_to_delete[key_position]).delete()
            logger.info('User deleted successfully')

            return success
        else:
            logger.error("User doesn't exists in DB")

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User wasn't deleted")

        return failure
