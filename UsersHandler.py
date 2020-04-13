from requests import RequestException

import DBHandler
import log
from consts import *

logger = log.setup_custom_logger()
firebase_db = DBHandler.get_firebase_db_ref()


def get_user_from_db(user_phone_number):
    logger.info('Trying to get user with phoneNumber=%s', user_phone_number)
    return firebase_db.child(users_collection).child(user_phone_number).get()


def login(user_data):
    logger.info('User with phoneNumber=%s trying to login', user_data[phone_number])

    try:
        logger.info('Trying to get user from DB')
        user = get_user_from_db(user_data[phone_number])

        if user is None:
            logger.info('''User doesn't exists in DB''')
            logger.info('Trying to create new user')

            # validate_user_is_real_soldier(user_data)
            firebase_db.child(users_collection).child(user_data[phone_number]).set(build_new_user_object(user_data))
            logger.info('Creation completed successfully')
            logger.info('Returning success')

            return success
        else:
            logger.info("User exists in DB")
            # validate_user_is_real_soldier(user_data)
            logger.info('Returning user')

            return user
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User login failed")

        return failure


def auto_login(user_phone_number):
    logger.info('User with phoneNumber=%s trying to auto login', user_phone_number)

    try:
        logger.info('Trying to get user from DB')
        user = get_user_from_db(user_phone_number)

        if user is None:
            logger.info('''User doesn't exists in DB''')
            return failure
        else:
            logger.info("User exists in DB")
            logger.info('Returning user')

            return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User login failed")

        return failure


def build_new_user_object(user_data):
    return {
        user_name: user_data[user_name],
        phone_number: user_data[phone_number],
        token: user_data[token],
    }


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


def add_ride_options_to_user(passenger, optional_offers):
    logger.info('Trying to get user all older offers from DB')
    passenger_offers = firebase_db.child(users_collection).child(passenger[phone_number]).child(rides).child(
        options).get()

    logger.info('Trying to insert all new optional offers and validating they are not exists already')

    for offer in optional_offers:
        if not user_already_has_this_offer(offer[key_position], passenger_offers):
            firebase_db.child(users_collection).child(passenger[phone_number]).child(rides).child(options).push(offer)

    logger.info('New offers insert successfully')


def user_already_has_this_offer(new_offer_id, passenger_offers):
    if passenger_offers is not None:
        for offer in passenger_offers:
            if passenger_offers[offer][key_position] == new_offer_id:
                return True

    return False


def print_list_of_users():
    all_users = firebase_db.child(users_collection).get()

    for user in all_users:
        logger.info('Name: %s, PhoneNumber: %s', all_users[user][user_name], all_users[user][phone_number])

    logger.info('Total %s users', len(all_users))


def validate_user_is_real_soldier(user_data):
    return True
