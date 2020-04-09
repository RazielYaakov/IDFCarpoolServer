import json

from flask import Flask, request

import RidesHandler
import UsersHandler
import log
from consts import phone_number, ride_ID, user_type, offer_id, request_id

app = Flask(__name__)
logger = log.setup_custom_logger()


def create_json_object_from_request_args(request_args):
    return {argument: request_args.get(argument) for argument in request_args}


@app.route('/')
def hello():
    return 'Raziel Yaakov Hamalic'


# completed
@app.route('/login', methods=['POST'])
def login_user():
    logger.info('Get request to login: ' + request.url)
    user_data = create_json_object_from_request_args(request.args)

    return UsersHandler.login(user_data)


#completed
@app.route('/newrideoffer', methods=['POST'])
def new_ride():
    logger.info('Get request to add new ride: ' + request.url)
    add_ride_request = create_json_object_from_request_args(request.args)

    return RidesHandler.add_ride_offer(add_ride_request)


# completed
@app.route('/findride', methods=['POST'])
def find_ride():
    logger.info('Get request to find ride: ' + request.url)
    find_ride_request = create_json_object_from_request_args(request.args)

    return json.dumps(RidesHandler.find_ride(find_ride_request))


# completed
@app.route('/showmyrides')
def show_user_ride_requests():
    logger.info('Get request to show user rides: ' + request.url)
    user_phone_number = request.args.get(phone_number)
    rides = RidesHandler.get_user_rides(user_phone_number)

    return json.dumps(rides)


# completed
@app.route('/passengerofferaccept', methods=['POST'])
def passenger_accept_offer():
    logger.info('Get request to accept ride offer: ' + request.url)
    accepted_offer_id = request.args.get(offer_id)
    passenger_phone_number = request.args.get(phone_number)

    return RidesHandler.passenger_offer_accept(accepted_offer_id, passenger_phone_number)


# completed
@app.route('/driverrequestaccept', methods=['POST'])
def driver_accept_request():
    logger.info('Get request to accept ride requests: ' + request.url)
    accepted_request_id = request.args.get(request_id)

    return RidesHandler.driver_request_accept(accepted_request_id)


# completed
@app.route('/cancelrequest', methods=['POST'])
def cancel_request():
    logger.info('Get request to accept ride requests: ' + request.url)
    canceled_request_id = request.args.get(request_id)

    return RidesHandler.cancel_ride_request(canceled_request_id)


# completed
@app.route('/updateuser', methods=['POST'])
def update_user():
    logger.info('Get request to update user: ' + request.url)
    updated_user_data = create_json_object_from_request_args(request.args)

    return UsersHandler.update_user(updated_user_data)


# completed
@app.route('/deleteuser', methods=['POST'])
def delete_user():
    logger.info('Get request to delete user: ' + request.url)
    id_of_user_to_delete = request.args.get(phone_number)

    return UsersHandler.delete_user(id_of_user_to_delete)


@app.route('/cancelride', methods=['POST'])
def cancel_ride():
    logger.info('Get request to cancel ride requests: ' + request.url)
    type_of_user = request.args.get(user_type)
    ride_id = request.args.get(ride_ID)

    return RidesHandler.cancel_ride(type_of_user, ride_id)




def add_junk_users(i):
    hour = 7
    minutes = 00

    driver = {
        "userType": "driver",
        "name": "razi",
        "phoneNumber": str(i),
        "leavingHomeTime": str(hour) + ":" + str(minutes),
        "leavingBaseTime": str(hour + 6) + ":" + str(minutes),
        "baseLocation": "a",
        "homeLocation": "b",
    }

    for x in range(i, i + 5):
        UsersHandler.login(driver)
        driver["phoneNumber"] = str(x)

    driver["baseLocation"] = "b"
    driver["homeLocation"] = "a"

    for x in range(i + 5, i + 10):
        UsersHandler.login(driver)
        driver["phoneNumber"] = str(x)


logger.info('Server has reloaded')
logger.info('Queen Dana Koren')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
