import DBHandler
import UsersHandler
import log
from consts import *
from requests import RequestException
from datetime import datetime
# import nexmo
#
# client = nexmo.Client(key='82a7fce6', secret='3dc02eec783b28cc')
#
# client.send_message({
#     'from': 'IDF Carpool',
#     'to': 'number',
#     'text': 'Hi!\n You have a ride request\n :)',
# })

logger = log.setup_custom_logger('RidesHandler')
firebase_db = DBHandler.get_firebase_db_ref()


def get_all_rides_from_db():
    logger.info('Trying to get all rides from DB')
    return firebase_db.child(rides_collection).get().items()


def find_a_ride(ride_request):
    optional_drivers = get_all_optional_drivers(ride_request)

    if optional_drivers:
        logger.info("Founded %s optional drivers for the ride", len(optional_drivers))
        logger.info("Returning the optional drivers")

        return optional_drivers
    else:
        logger.info("No optional drivers for this ride")

        return None


def get_all_optional_drivers(ride_request):
    all_users = UsersHandler.get_all_users_from_db()
    logger.info('Trying to get the optional drivers')
    optional_drivers = []

    for user in all_users:
        if user[values_position].get(user_type) == driver_type and \
                is_driver_is_optional(user[values_position], ride_request):
            optional_drivers.append(user)
            if len(optional_drivers) > max_optional_drivers:
                break

    return optional_drivers


def is_driver_is_optional(driver, ride_request):
    return driver.get(leaving_time) == ride_request.get(leaving_time) and \
           driver.get(base_location) == ride_request.get(base_location) and \
           driver.get(home_location) == ride_request.get(wanted_location)


def create_ride(ride_request):
    logger.info('Trying to create new ride in DB')

    try:
        if is_ride_already_exists(ride_request):
            logger.error("Ride already exists in DB")
            logger.error("New ride wasn't created")

            return "Ride already exists in DB"
        else:
            logger.info("Ride doesn't exists in DB")
            logger.info('Trying to insert the ride to DB')

            firebase_db.child(rides_collection).push(ride_request)

            logger.info('Ride creation completed successfully')

            return 'Ride creation completed successfully'
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't created")

        return "Ride wasn't created"


def get_ride_from_db(ride_id):
    return firebase_db.child(rides_collection).child(ride_id)


def cancel_ride(ride_id):
    logger.info('Trying to cancel ride request')

    try:
        logger.info('Trying to get ride from DB')
        ride_to_delete = get_ride_from_db(ride_id)
        if ride_to_delete is not None:
            logger.info('Trying to delete ride request from DB')
            firebase_db.child(rides_collection).child(ride_id).delete()
            logger.info('Ride deleted successfully')

            return 'Ride deleted successfully'
        else:
            logger.error("Ride doesn't exists in DB")

            return "Ride doesn't exists in DB"
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't deleted")

        return "Ride wasn't deleted"


def accept_ride(ride_request, ride_id):
    logger.info('Trying to accept ride request')

    try:
        logger.info('Trying to get ride from DB')
        ride_to_accept = get_ride_from_db(ride_id)

        if ride_to_accept is not None:
            logger.info('Trying to accept ride request from DB')
            firebase_db.child(rides_collection).child(ride_id).update(ride_request)
            logger.info('Ride accepted successfully')

            return 'Ride accepted successfully'
        else:
            logger.error("Ride doesn't exists in DB")

            return "Ride doesn't exists in DB"
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't accepted")

        return "Ride wasn't accepted"


def is_same_ride_request(ride, ride_request):
    return ride.get(driver_phone_number) == ride_request.get(driver_phone_number) and \
           ride.get(passenger_phone_number) == ride_request.get(passenger_phone_number) and \
           ride.get(base_location) == ride_request.get(base_location) and \
           ride.get(wanted_location) == ride_request.get(wanted_location) and \
           ride.get(date) == ride_request.get(date)


def is_ride_already_exists(ride_request):
    logger.info('Checking if ride already exists in DB')
    all_rides = get_all_rides_from_db()

    for ride in all_rides:
        if is_same_ride_request(ride[values_position], ride_request):
            return True

    return False


def is_ride_time_passed(this_day, ride_date):
    return False


def get_user_ride_requests(user_id):
    all_rides = get_all_rides_from_db()
    rider = UsersHandler.get_user_from_db(user_id)
    user_rides = []

    for ride in all_rides.items():
        if ride[values_position].get(passenger_phone_number) == user_id:
            user_rides.append(ride)

    return user_rides


def get_all_irrelevant_rides():
    logger.info('Trying to get all rides from DB')
    all_rides = get_all_rides_from_db()
    this_day = datetime.now()
    irrelevant_rides = []

    for ride in all_rides.items():
        if is_ride_time_passed(this_day, ride[values_position].get(date)):
            irrelevant_rides.append(ride)

    return irrelevant_rides


def delete_irrelevant_rides():
    logger.info('Trying to delete from DB all rides that their date is passed')
    rides_to_delete = get_all_irrelevant_rides()

    for irrelevant_ride in rides_to_delete:
        firebase_db.child(rides_collection).child(irrelevant_ride[key_position]).delete()

    logger.info('Irrelevant rides deleted successfully')
