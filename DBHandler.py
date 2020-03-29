from firebase import Firebase
from requests import RequestException

import log
from consts import *

logger = log.setup_custom_logger('DBHandler')

# firebase config
firebase_config = {
    "apiKey": "AIzaSyCkYngiJhQe9V7xlBsPIJzAf5quI2SBIFA",
    "authDomain": "carpool-832da.firebaseapp.com",
    "databaseURL": "https://carpool-832da.firebaseio.com",
    "projectId": "carpool-832da",
    "storageBucket": "carpool-832da.appspot.com",
    "messagingSenderId": "212737775848",
    "appId": "1:212737775848:web:ef89caf857c04538d1915d",
    "measurementId": "G-VB5385FGM7"
}
firebase = Firebase(firebase_config)
auth = firebase.auth()
logged_user = auth.sign_in_with_email_and_password(user_email, user_password)
firebase_db = firebase.database()


def get_all_users_from_db():
    return firebase_db.child(users_collection).get()


def is_user_exist_in_db(user_id):
    logger.info('Check if user with phone-number=%s exists in DB', user_id)

    all_users = get_all_users_from_db()

    for user in all_users.each():
        if user.val().get(phone_number) == user_id:
            logger.info('User exists in DB')
            return True

    return False


def get_user_from_db(user_id):
    if is_user_exist_in_db(user_id):
        all_users = firebase_db.child(users_collection).get()

        for user in all_users.each():
            if user.val().get(phone_number) == user_id:
                return user
    else:
        raise RequestException("User doesn't exists in DB")


def create_new_user(new_user_data):
    logger.info('Trying to create new user in DB')

    try:
        if is_user_exist_in_db(new_user_data.get(phone_number)):
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
        logger.info('Trying to update user data')
        firebase_db.child(users_collection).child(user_old_data.key()).update(user_updated_data)
        logger.info('Update user completed successfully')

        return 'Update user completed successfully'
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User doesn't updated")
        return 'User does not updated'


def delete_user(user_id):
    logger.info('Trying to delete user with phone_number=%s from DB', user_id)

    try:
        logger.info('Trying to get user from DB')
        user_to_delete = get_user_from_db(user_id)
        logger.info('Trying to delete user')

        firebase_db.child(users_collection).child(user_to_delete.key()).remove()

        logger.info('User deleted successfully')

        return 'User deleted successfully'
    except RequestException as err:
        logger.error(str(err))
        logger.warning("User wasn't deleted")

        return "User wasn't deleted"


def get_all_users_with_specific_routes_and_hour(source_point, destination_point, leaving_hour):
    logger.info('Searches for all drivers that are leave from %s and going to to %s at time %s',
                source_point, destination_point, leaving_hour)
    all_users = get_all_users_from_db()
    matching_users = []

    for user in all_users.each():
        if user.val().get(user_type) == driver_type:
            if user.val().get(source) == source_point and leaving_hour == user.val().get(leaving_time) and \
                    user.val().get(destination) == destination_point:
                matching_users.append(user.val())

    return matching_users
