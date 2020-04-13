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
    driver = UsersHandler.get_user_from_db(ride_offer[phone_number])

    try:
        if driver is not None:
            offer_object = build_ride_offer_object(ride_offer, driver)
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


def build_ride_offer_object(ride_offer, driver):
    return {
        source: ride_offer[source],
        destination: ride_offer[destination],
        date: str(arrow.get(ride_offer[date])),
        phone_number: driver[phone_number],
        user_name: driver[user_name],
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
    if offer_from_db is not None:
        return offer_from_db[phone_number] == new_ride_offer[phone_number] and \
               offer_from_db[source] == new_ride_offer[source] and \
               offer_from_db[destination] == new_ride_offer[destination] and \
               offer_from_db[permanent_offer] == new_ride_offer[permanent_offer] and \
               offer_from_db[date] == str(arrow.get(new_ride_offer[date]))

    return False


def find_ride(ride_request):
    passenger = UsersHandler.get_user_from_db(ride_request[phone_number])

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
                optional_offers.append({offer_id: optional_offer_id, offer_data: offers_from_source[optional_offer_id]})

    return optional_offers


def is_optional_offer(optional_offer, ride_request):
    return optional_offer[phone_number] != ride_request[phone_number] and \
           optional_offer[destination] == ride_request[destination] and \
           is_matching_hours(optional_offer[date], str(arrow.get(ride_request[date])),
                             optional_offer[permanent_offer])


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
            all_user_rides = get_user_rides_from_pointers(user_rides_pointers)
            logger.info('Found %s rides, returning them to user', len(all_user_rides))

            return all_user_rides
        else:
            logger.error('No user with id=%s', user_phone_number)

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning('''There was an error while trying to get user rides from DB''')

        return failure


def get_user_rides_from_pointers(user_rides_pointers):
    if user_rides_pointers is not None:
        user_offers = user_rides_pointers.get(offers_collection)
        user_requests = user_rides_pointers.get(requests_collection)

        return {offers_collection: get_offers_from_pointers(user_offers),
                requests_collection: get_requests_from_pointers(user_requests)}

    return {}


def get_offers_from_pointers(pointers):
    offers = []

    if pointers is not None:
        for pointer in pointers:
            offers.append({offer_id: pointers[pointer][offer_id],
                           offer_data: firebase_db.child(rides_collection).child(offers_collection).
                          child(pointers[pointer][offer_id]).get()})

    return offers


def get_requests_from_pointers(pointers):
    requests = []

    if pointers is not None:
        requests_as_driver = get_requests_of_type(pointers.get(as_driver))
        requests_as_passenger = get_requests_of_type(pointers.get(as_passenger))

        requests = {as_driver: requests_as_driver, as_passenger: requests_as_passenger}

    return requests


def get_requests_of_type(pointers):
    requests = []

    if pointers is not None:
        for pointer in pointers:
            requests.append({request_id: pointers[pointer][request_id],
                             request_data: firebase_db.child(rides_collection).child(requests_collection).
                            child(pointers[pointer][request_id]).get()})

    return requests


def passenger_offer_accept(accepted_offer_id, passenger_phone_number):
    logger.info('Passenger trying to accept ride offer')
    passenger = UsersHandler.get_user_from_db(passenger_phone_number)

    try:
        if passenger is not None:
            accepted_offer = get_offer_from_db(accepted_offer_id)

            if accepted_offer is not None:
                if not is_passenger_accepted_this_offer_already(passenger_phone_number, accepted_offer_id):
                    logger.info('Trying to create ride request')
                    new_request = build_ride_request_object(accepted_offer, passenger)
                    new_request_response = firebase_db.child(rides_collection).child(requests_collection).push(
                        new_request)
                    add_request_to_users_rides(passenger_phone_number, accepted_offer[phone_number],
                                               new_request_response.key, accepted_offer_id)
                    logger.info('Sending push notification to driver about new ride request')
                    send_push_notification_new_ride_request_to_driver(passenger, accepted_offer[phone_number])

                logger.info('Returning success')
                return success
            else:
                logger.error('''Offer with id=%s doesn't exists''', accepted_offer_id)
                return failure
        else:
            logger.error('''User with phoneNumber=%s doesn't exists''', passenger_phone_number)
            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Offer wasn't accepted")

        return failure


def is_passenger_accepted_this_offer_already(passenger_phone_number, accepted_offer_id):
    logger.info('Validating if user not accept this offer already')
    user_requests_as_passenger = firebase_db.child(users_collection).child(passenger_phone_number). \
        child(rides_collection).child(requests_collection).child(as_passenger).get()

    if user_requests_as_passenger is not None:
        for request_as_passenger in user_requests_as_passenger:
            if user_requests_as_passenger[request_as_passenger][offer_id] == accepted_offer_id:
                logger.info('Offer already accepted by user!')
                return True

    return False


def get_offer_from_db(wanted_offer_id):
    logger.info('Trying to get offer from DB')
    wanted_offer = firebase_db.child(rides_collection).child(offers_collection).child(wanted_offer_id).get()

    if wanted_offer is not None:
        return wanted_offer

    logger.error('''Offer doesn't exists in DB''')
    return None


def add_request_to_users_rides(passenger_phone_number, driver_phone_number, new_request_id, accepted_offer_id):
    logger.info('Trying to insert the request id to passenger and driver rides')

    try:
        firebase_db.child(users_collection).child(passenger_phone_number).child(rides).child(
            requests_collection).child(as_passenger).push({request_id: new_request_id, offer_id: accepted_offer_id})
        firebase_db.child(users_collection).child(driver_phone_number).child(rides).child(
            requests_collection).child(as_driver).push({request_id: new_request_id})
        logger.info("Insert completed successfully")
    except RequestException as err:
        logger.error(str(err))
        logger.error("Insert failed")


def build_ride_request_object(accepted_offer, passenger):
    return {
        source: accepted_offer[source],
        destination: accepted_offer[destination],
        date: str(arrow.get(accepted_offer[date])),
        driver_type: {
            phone_number: accepted_offer[phone_number],
            user_name: accepted_offer[user_name],
            accepted: False
        },
        passenger_type: {
            phone_number: passenger[phone_number],
            user_name: passenger[user_name],
            accepted: True
        },
        accepted: False
    }


def driver_request_accept(accepted_request_id):
    logger.info('Driver trying to accept ride request')
    accepted_request = get_request_from_db(accepted_request_id)

    try:
        if accepted_request is not None:
            logger.info('''Trying to chance driver's request accept status in DB to True''')
            firebase_db.child(rides_collection).child(requests_collection).child(accepted_request_id).child(
                driver_type).child(accepted).set(True)
            logger.info('Driver accept status changed successfully')

            logger.info('Sending push notification to passenger about driver accepted request')
            send_push_notification_ride_request_approved_by_driver(accepted_request[passenger_type][phone_number])
            logger.info('Returning success')

            return success
        else:
            logger.error('''Request with id=%s doesn't exists''', accepted_request_id)

            return failure
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Request wasn't accepted")

        return failure


def get_request_from_db(wanted_request_id):
    logger.info('Trying to get request from DB')
    wanted_request = firebase_db.child(rides_collection).child(requests_collection).child(wanted_request_id).get()

    if wanted_request is not None:
        return wanted_request

    logger.error('''Request doesn't exists in DB''')
    return None


def passenger_handshake(accepted_request_id):
    logger.info('Passenger trying to make handshake to deal request %s', accepted_request_id)
    request = get_request_from_db(accepted_request_id)

    try:
        if request is None:
            logger.error('''Request %s doesn't exists in DB''', accepted_request_id)
            return failure

        firebase_db.child(rides_collection).child(requests_collection).child(accepted_request_id).child(accepted).set(
            True)
        logger.info('Handshake completed successfully')

        logger.info('Sending push notification to driver about ride approved by passenger')
        send_push_notification_ride_approved_by_passenger(request)
        logger.info('Returning success')

        return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Handshake wasn't happen")

        return failure


def cancel_ride_request(request_to_cancel_id, user_phone_number):
    logger.info('Trying to cancel ride request %s', request_to_cancel_id)
    request_to_cancel = get_request_from_db(request_to_cancel_id)

    try:
        if request_to_cancel is None:
            return failure

        delete_request_from_users(request_to_cancel, request_to_cancel_id)
        delete_request_from_requests_collection(request_to_cancel_id)

        logger.info('Sending push notification about canceling ride')
        send_push_notification_about_ride_canceled(request_to_cancel, user_phone_number)
        logger.info('Return success')

        return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Request wasn't deleted")

        return failure


def delete_request_from_users(request_to_cancel, request_to_cancel_id):
    logger.info('Trying to delete requests from users')
    passenger_phone_number = request_to_cancel[passenger_type][phone_number]
    driver_phone_number = request_to_cancel[driver_type][phone_number]

    try:
        delete_request_from_user(passenger_phone_number, request_to_cancel_id, is_passenger=True)
        delete_request_from_user(driver_phone_number, request_to_cancel_id, is_passenger=False)

        logger.info("Delete from user rides completed successfully")
    except RequestException as err:
        logger.error(str(err))
        logger.error("Insert failed")


def delete_request_from_user(user_phone_number, request_to_cancel_id, is_passenger):
    as_user_type = (as_driver, as_passenger)[is_passenger]

    try:
        request_do_delete = firebase_db.child(users_collection).child(user_phone_number). \
            child(rides).child(requests_collection).child(as_user_type).order_by_child(request_id). \
            equal_to(request_to_cancel_id).get()

        for key in request_do_delete.keys():
            firebase_db.child(users_collection).child(user_phone_number).child(rides).child(requests_collection).child(
                as_user_type).child(key).delete()
            logger.info('Request deleted from user %s rides', user_phone_number)

    except RequestException as err:
        logger.error(str(err))
        logger.error("Delete request from user %s failed", user_phone_number)


def delete_request_from_requests_collection(request_to_cancel_id):
    logger.info('Trying to delete request from requests collection')

    try:
        firebase_db.child(rides_collection).child(requests_collection).child(request_to_cancel_id).delete()
        logger.info('Request deleted successfully from requests collection')
    except RequestException as err:
        logger.error(str(err))
        logger.error("Delete request from requests collection failed")


def cancel_ride_offer(offer_to_cancel_id):
    logger.info('Trying to cancel ride offer %s', offer_to_cancel_id)
    offer_to_cancel = get_offer_from_db(offer_to_cancel_id)

    try:
        if offer_to_cancel is None:
            return failure

        delete_offer_from_users(offer_to_cancel[phone_number], offer_to_cancel_id)
        delete_offer_from_offers_collection(offer_to_cancel_id)

        return success
    except RequestException as err:
        logger.error(str(err))
        logger.warning("Offer wasn't deleted")

        return failure


def delete_offer_from_users(user_phone_number, offer_to_cancel_id):
    logger.info('Trying to delete offer from driver %s', user_phone_number)

    try:
        offer_do_delete = firebase_db.child(users_collection).child(user_phone_number). \
            child(rides).child(offers_collection).order_by_child(offer_id). \
            equal_to(offer_to_cancel_id).get()

        for key in offer_do_delete.keys():
            firebase_db.child(users_collection).child(user_phone_number).child(rides).child(offers_collection). \
                child(key).delete()
            logger.info('Offer deleted from user %s rides', user_phone_number)

    except RequestException as err:
        logger.error(str(err))
        logger.error("Delete request from user %s failed", user_phone_number)


def delete_offer_from_offers_collection(offer_to_cancel_id):
    logger.info('Trying to delete offer from offers collection')

    try:
        firebase_db.child(rides_collection).child(offers_collection).child(offer_to_cancel_id).delete()
        logger.info('Offer deleted successfully from offers collection')
    except RequestException as err:
        logger.error(str(err))
        logger.error("Delete offer from offer collection failed")


def send_push_notification_new_ride_request_to_driver(passenger, driver_phone_number):
    driver = UsersHandler.get_user_from_db(driver_phone_number)

    if is_valid_token(driver):
        PushNotificationsHandler.send_push_notification(driver[token],
                                                        passenger[user_name] + ' רוצה לנסוע איתך, חבל לנסוע לבד')


def send_push_notification_ride_request_approved_by_driver(passenger_phone_number):
    passenger = UsersHandler.get_user_from_db(passenger_phone_number)

    if is_valid_token(passenger):
        PushNotificationsHandler.send_push_notification(passenger[token], 'אישרו לך טרמפ, לא תכנס לבדוק מי?')


def send_push_notification_ride_approved_by_passenger(request):
    driver = UsersHandler.get_user_from_db(request[driver_type][phone_number])

    if is_valid_token(driver):
        PushNotificationsHandler. \
            send_push_notification(driver[token],
                                   request[passenger_type][user_name] + ' מצטרף אליך סופית, אל תשכח אותו כשתצא')


def send_push_notification_about_ride_canceled(request_to_cancel, canceler_phone_number):
    phone_number_to_send_notification = \
        (request_to_cancel[passenger_type][phone_number], request_to_cancel[driver_type][phone_number])[
            request_to_cancel[passenger_type][phone_number] == canceler_phone_number]

    user = UsersHandler.get_user_from_db(phone_number_to_send_notification)

    if is_valid_token(user):
        PushNotificationsHandler.send_push_notification(user[token], get_cancel_message(request_to_cancel))


def get_cancel_message(request_to_cancel):
    cancel_message = 'שים לב, הטרמפ שלך מ' + request_to_cancel[source] + ' ל' + request_to_cancel[destination] + \
                     ' בוטל'

    return cancel_message


def is_valid_token(user):
    logger.info('Validating user token')
    user_token = user.get(token)

    if user_token is not None:
        if expo_token in user_token:
            logger.info('User token is valid, sending notification')
            return True

    logger.info('User token is invalid, not sending notification')
    return False
