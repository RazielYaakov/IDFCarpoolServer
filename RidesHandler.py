import arrow
import dateutil.parser
from requests import RequestException

import DBHandler
import PushNotificationsHandler
import UsersHandler
import log
from consts import *

logger = log.setup_custom_logger()
firebase_db = DBHandler.get_firebase_db_ref()


def add_ride_offer(ride_offer):
    logger.info('Trying to build ride offer object')
    offer_object = build_ride_offer_object(ride_offer)
    driver = UsersHandler.get_user_from_db(ride_offer[driver_phone_number])

    try:
        if driver is not None:
            if is_offer_exists_already(driver, offer_object):
                logger.warning('Offer already exists in DB, not creating a new one')

                return offer_already_exists
            else:
                logger.info('Trying to insert new offer to DB')
                new_offer = firebase_db.child(rides_collection).child(offers_collection).push(offer_object)
                firebase_db.child(users_collection).child(driver[phone_number]).child(rides). \
                    child(offers_collection).push({offer_id: new_offer.key})
                logger.info('Offer insert completed successfully')
                return success
        else:
            logger.error('''Driver doesn't exists!''')

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Offer creation failed")

        return failure


def build_ride_offer_object(ride_offer):
    return {
        source: ride_offer[source],
        destination: ride_offer[destination],
        date: str(arrow.get(ride_offer[date]).to(time_zone)),
        driver_phone_number: ride_offer[driver_phone_number],
        permanent_offer: ride_offer[permanent_offer]
    }


def is_offer_exists_already(driver, offer_object):
    logger.info('Checking if the offer is already exists in DB')
    driver_offers = firebase_db.child(users_collection).child(driver[phone_number]).child(rides).child(
        offers_collection).get()

    if driver_offers is not None:
        for curr_offer in driver_offers:
            offer_from_db = firebase_db.child(rides).child(offers_collection).child(
                driver_offers[curr_offer][offer_id]).get()
            if is_same_offer(offer_from_db, offer_object):
                return True

    logger.info('''Offer doesn't exists''')
    return False


def is_same_offer(offer_from_db, new_ride_offer):
    return offer_from_db[driver_phone_number] == new_ride_offer[driver_phone_number] and \
           offer_from_db[source] == new_ride_offer[source] and \
           offer_from_db[destination] == new_ride_offer[destination] and \
           offer_from_db[permanent_offer] == new_ride_offer[permanent_offer] and \
           offer_from_db[date] == new_ride_offer[date]


def find_ride(ride_request):
    passenger = UsersHandler.get_user_from_db(ride_request[phone_number])
    optional_offers = []

    if passenger is None:
        logger.error('''User doesn't exists''')
        return None

    logger.info('Trying to find optional ride offers')
    optional_offers = get_optional_offers(ride_request)

    if len(optional_offers) == 0:
        logger.info('No optional offers')
        return optional_offers

    logger.info('%s optional offers founded, sending them to user', len(optional_offers))

    return optional_offers


def get_optional_offers(ride_request):
    offers_from_source = firebase_db.child(rides_collection).child(offers_collection). \
        order_by_child(source).equal_to(ride_request[source]).get()
    optional_offers = []

    if offers_from_source is not None:
        for optional_offer_id in offers_from_source:
            if is_optional_offer(offers_from_source[optional_offer_id], ride_request):
                optional_offers.append([optional_offer_id, offers_from_source[optional_offer_id]])

    return optional_offers


def is_optional_offer(optional_offer, ride_request):
    return optional_offer[driver_phone_number] != ride_request[phone_number] and \
           optional_offer[destination] == ride_request[destination] and \
           is_matching_hours(optional_offer[date], ride_request[date], optional_offer[permanent_offer])


def is_matching_hours(offer_time, requested_time, is_permanent_offer):
    return calc_time_difference_in_minutes(offer_time, requested_time) <= 60 and \
           is_same_date(offer_time, requested_time, is_permanent_offer)


def calc_time_difference_in_minutes(offer_time, requested_time):
    time_delta = get_time_delta(offer_time, requested_time)

    if time_delta.days < 0:
        time_delta = time_delta * (-1)

    delta_in_minutes = time_delta.seconds / 60

    return delta_in_minutes


def is_same_date(offer_time, requested_time, is_permanent_offer):
    if not is_permanent_offer:
        delta = get_time_delta(offer_time, requested_time)
        return delta.days == 0 or abs(delta.days) == 1

    return True


def get_time_delta(offer_time, requested_time):
    return dateutil.parser.isoparse(offer_time) - dateutil.parser.isoparse(requested_time)


def get_user_rides(user_phone_number):
    user = UsersHandler.get_user_from_db(user_phone_number)

    try:
        if user is not None:
            logger.info('Trying to get all rides of user with id=%s', user_phone_number)
            user_rides_pointers = firebase_db.child(users_collection).child(user_phone_number).child(rides).get()

            return get_user_rides_from_pointers(user_rides_pointers)
        else:
            logger.error('No user with id=%s', user_phone_number)

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning('''There was an error while trying to get user rides from DB''')

        return failure


def get_user_rides_from_pointers(user_rides_pointers):
    user_offers = user_rides_pointers.get(offers_collection)
    user_requests = user_rides_pointers.get(requests_collection)

    return {offers_collection: get_objects_from_pointers(user_offers, offers_collection),
            requests_collection: get_objects_from_pointers(user_requests, requests_collection)}


def get_objects_from_pointers(pointers, collection_name):
    objects = []
    id_name = (offer_id, request_id)[collection_name == requests_collection]

    if pointers is not None:
        for pointer in pointers:
            objects.append(firebase_db.child(rides_collection).child(collection_name).
                           child(pointers[pointer][id_name]).get())

    return objects


def accept_ride(type_of_user, ride_id):
    logger.info('Trying to accept ride request')

    try:
        logger.info('Trying to get ride from DB')
        ride_to_accept = get_ride_from_db(ride_id)

        if ride_to_accept is not None:
            logger.info('Trying to accept ride request from DB')
            if ride_to_accept[1][driver_type][accepted] == True and ride_to_accept[1][passenger_type][
                accepted] == True and type_of_user == passenger_type:
                firebase_db.child(rides_collection).child(ride_id).child(accepted).set(True)
                logger.info('Ride accepted successfully by both passenger and driver')
            else:
                firebase_db.child(rides_collection).child(ride_id).child(type_of_user).child(accepted).set(True)
                logger.info('Ride accepted successfully by %s', type_of_user)

            send_accept_push_notification_to_other_user(ride_id)

            return success
        else:
            logger.error("Ride doesn't exists in DB")

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't accepted")

        return failure


def get_all_ride_offers_from_db():
    logger.info('Trying to get all ride offers from DB')
    all_offers = firebase_db.child(rides_collection).child(offers_collection).get()

    if all_offers is not None:
        return all_offers.items()

    return None


def get_all_rides_from_db():
    logger.info('Trying to get all rides from DB')
    all_rides = firebase_db.child(rides_collection).get()

    if all_rides is not None:
        return all_rides.items()

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

            ride = {}
            ride_id = firebase_db.child(rides_collection).push(ride)
            ride[ride_ID] = ride_id.key

            logger.info('Ride creation completed successfully')

            return ride
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't created")

        return failure


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
            send_cancel_push_notification_to_other_user(ride_to_delete, type_of_user)
            return success
        else:
            logger.error("Ride doesn't exists in DB")

            return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Ride wasn't deleted")

        return failure


def send_cancel_push_notification_to_other_user(ride, cancelled_user_type):
    cancelled_user = ride[1][cancelled_user_type]
    other_user = ride[1][get_other_user_type(cancelled_user_type)]

    if other_user[accepted]:
        if cancelled_user_type == passenger_type:
            PushNotificationsHandler.send_push_notification(other_user[token],
                                                            cancelled_user[user_name] + ' ביטל את הטרמפ, אל תחכה לו')
        elif cancelled_user_type == driver_type:
            PushNotificationsHandler.send_push_notification(other_user[token], 'לא מסתדר ל' + cancelled_user[
                user_name] + ' להסיע אותך, חפש שוב טרמפ')


def get_other_user_type(type_of_user):
    return (driver_type, passenger_type)[type_of_user == driver_type]


def send_accept_push_notification_to_other_user(ride_id):
    ride_accepted = firebase_db.child(rides_collection).child(ride_id).child(accepted).get()
    driver = firebase_db.child(rides_collection).child(ride_id).child(driver_type).get()
    passenger = firebase_db.child(rides_collection).child(ride_id).child(passenger_type).get()

    if ride_accepted:
        if not driver[accepted] and passenger[accepted]:
            PushNotificationsHandler.send_push_notification(driver[token],
                                                            passenger[user_name] + ' רוצה לנסוע איתך, חבל לנסוע לבד')
        elif driver[accepted] and passenger[accepted]:
            PushNotificationsHandler.send_push_notification(passenger[token],
                                                            driver[user_name] + ' סבבה עם בקשת הנסיעה שלך')
    else:
        PushNotificationsHandler.send_push_notification(driver[token], passenger[
            user_name] + ' מצטרף אליך סופית, אל תשכח אותו כשאתה יוצא')
