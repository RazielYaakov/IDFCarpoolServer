from datetime import datetime

import arrow
from requests import RequestException

import DBHandler
import UsersHandler
import log
from consts import *

logger = log.setup_custom_logger()
firebase_db = DBHandler.get_firebase_db_ref()


def get_all_rides_from_db():
    logger.info('Trying to get all rides from DB')
    all_rides = firebase_db.child(rides_collection).get()

    if all_rides is not None:
        return all_rides.items()

    return None


def parse_time_to_hour_minutes_seconds(ride_time):
    logger.info('Trying to parse time to H:M format')
    parsed_ride_hour = arrow.get(ride_time).to(time_zone).datetime.hour
    parsed_ride_minutes = arrow.get(ride_time).to(time_zone).datetime.minute

    return str(parsed_ride_hour) + ':' + str(parsed_ride_minutes)


def calc_time_difference_in_minutes(driver_time, ride_time):
    parsed_ride_time = parse_time_to_hour_minutes_seconds(ride_time)

    time_format = '%H:%M'
    time_diff = datetime.strptime(parsed_ride_time, time_format) - datetime.strptime(driver_time, time_format)
    if time_diff.days < 0:
        time_diff = datetime.strptime(driver_time, time_format) - datetime.strptime(parsed_ride_time, time_format)

    return time_diff.seconds / 60


def is_matching_hours(driver_time, ride_time):
    return calc_time_difference_in_minutes(driver_time, ride_time) <= 60


def is_driver_is_optional(driver, ride_request):
    if ride_request.get(home_to_base):
        return driver.get(home_location) == ride_request.get(source) and \
               driver.get(base_location) == ride_request.get(destination) and \
               is_matching_hours(driver.get(leaving_home_time), ride_request.get(date))
    else:
        return driver.get(base_location) == ride_request.get(source) and \
               driver.get(home_location) == ride_request.get(destination) and \
               is_matching_hours(driver.get(leaving_base_time), ride_request.get(date))


def get_all_optional_drivers(ride_request):
    all_users = UsersHandler.get_all_users_from_db()
    logger.info('Trying to get the optional drivers for ride')
    optional_drivers = []

    for user in all_users:
        if user[values_position].get(user_type) == driver_type and \
                is_driver_is_optional(user[values_position], ride_request):
            optional_drivers.append(user)

    # filter_drivers_by_matching_time(optional_drivers, ride_request.get(date))

    return optional_drivers


def find_ride(ride_request):
    optional_drivers = get_all_optional_drivers(ride_request)
    passenger = UsersHandler.get_user_from_db(ride_request.get(phone_number))

    if optional_drivers:
        logger.info("Founded %s optional drivers for the ride", len(optional_drivers))
        logger.info("Returning the optional rides")

        return create_optional_rides(ride_request, passenger, optional_drivers)

    logger.info("No optional drivers for this ride")

    return None


def create_optional_rides(ride_request, passenger, optional_drivers):
    logger.info('Trying to create rides')
    optional_rides = []

    for driver in optional_drivers:
        optional_ride = create_ride(ride_request, passenger, driver)

        if optional_ride is not None:
            optional_rides.append(optional_ride)

            if len(optional_rides) == max_optional_drivers:
                break

    return optional_rides


def create_ride(ride_request, passenger, driver):
    logger.info('Trying to create new ride in DB')

    try:
        if is_ride_already_exists(ride_request, passenger, driver):
            logger.error("Ride already exists in DB")
            logger.error("New ride wasn't created")

            return None
        else:
            logger.info("Ride doesn't exists in DB")
            logger.info('Trying to insert the ride to DB')

            ride = build_ride_object(ride_request, passenger, driver)
            ride_id = firebase_db.child(rides_collection).push(ride)
            ride[ride_ID] = ride_id.key

            logger.info('Ride creation completed successfully')

            return ride
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't created")

        return failure


def build_ride_object(ride_request, passenger, driver):
    return {
        driver_type: {
            user_name: driver[values_position].get(user_name),
            phone_number: driver[values_position].get(phone_number),
            accepted: False,
        },
        passenger_type: {
            user_name: passenger[values_position].get(user_name),
            phone_number: passenger[values_position].get(phone_number),
            accepted: False,
        },
        source: ride_request.get(source),
        destination: ride_request.get(destination),
        date: str(arrow.get(ride_request.get(date)).to(time_zone)),
        accepted: False
    }


def is_ride_already_exists(ride_request, passenger, driver):
    logger.info('Checking if ride already exists in DB')
    all_rides = get_all_rides_from_db()

    if all_rides is not None:
        for ride in all_rides:
            if is_same_ride_request(ride[values_position], ride_request, passenger, driver):
                return True

    return False


def is_same_ride_request(ride, ride_request, passenger, driver):
    return ride.get(passenger_type).get(phone_number) == passenger[values_position].get(phone_number) and \
           ride.get(driver_type).get(phone_number) == driver[values_position].get(phone_number) and \
           ride.get(source) == ride_request.get(source) and \
           ride.get(destination) == ride_request.get(destination) and \
           ride.get(date) == arrow.get(ride_request.get(date)).to(time_zone)


def get_ride_from_db(ride_id):
    logger.info('Trying to find ride with id=%s', ride_id)
    all_rides = get_all_rides_from_db()

    if all_rides is not None:
        for ride in all_rides:
            if ride[key_position] == ride_id:
                logger.info('Ride founded')
                return ride

    return None


def cancel_ride(type_of_user, ride_id):
    logger.info('Trying to cancel ride request')

    try:
        logger.info('Trying to get ride from DB')
        ride_to_delete = get_ride_from_db(ride_id)
        if ride_to_delete is not None:
            logger.info('Trying to delete ride request from DB')
            firebase_db.child(rides_collection).child(ride_id).delete()
            logger.info('Ride deleted successfully')
            # push notification to the other user said that the ride is canceled
            return success
        else:
            logger.error("Ride doesn't exists in DB")

            return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't deleted")

        return failure


def accept_ride(type_of_user, ride_id):
    logger.info('Trying to accept ride request')

    try:
        logger.info('Trying to get ride from DB')
        ride_to_accept = get_ride_from_db(ride_id)

        if ride_to_accept is not None:
            logger.info('Trying to accept ride request from DB')

            firebase_db.child(rides_collection).child(ride_id).child(type_of_user).child(accepted).set(True)

            logger.info('Ride accepted successfully')
            # send push notification to other user
            return success
        else:
            logger.error("Ride doesn't exists in DB")

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't accepted")

        return failure


# relevant until we have push notification - for update ride status in client side
def get_user_ride_requests(type_of_user, user_id):
    all_rides = get_all_rides_from_db()
    user_rides = []
    
    if all_rides is not None:
        for ride in all_rides:
            if ride[values_position].get(type_of_user).get(phone_number) == user_id:
                user_rides.append(ride)

    return user_rides


def is_ride_time_passed(this_day, ride_date):
    return False


def get_all_irrelevant_rides():
    logger.info('Trying to get all rides from DB')
    all_rides = get_all_rides_from_db()
    this_day = datetime.now()
    irrelevant_rides = []

    for ride in all_rides:
        if is_ride_time_passed(this_day, ride[values_position].get(date)):
            irrelevant_rides.append(ride)

    return irrelevant_rides


def delete_irrelevant_rides():
    logger.info('Trying to delete from DB all rides that their date is passed')
    rides_to_delete = get_all_irrelevant_rides()

    for irrelevant_ride in rides_to_delete:
        firebase_db.child(rides_collection).child(irrelevant_ride[key_position]).delete()

    logger.info('Irrelevant rides deleted successfully')
