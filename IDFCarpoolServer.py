import json

from flask import Flask, request

import RidesHandler
import UsersHandler
import log
from consts import phone_number, ride_ID

app = Flask(__name__)
logger = log.setup_custom_logger()


def create_json_object_from_request_args(request_args):
    return {argument: request_args.get(argument) for argument in request_args}


@app.route('/')
def hello():
    return 'Raziel Yaakov'


# completed
@app.route('/createuser', methods=['POST'])
def create_new_user():
    logger.info('Get request to create new user: ' + request.url)
    new_user_data = create_json_object_from_request_args(request.args)

    return UsersHandler.create_new_user(new_user_data)


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


# completed
@app.route('/restoreuser', methods=['POST'])
def restore_user():
    logger.info('Get request to restore user: ' + request.url)
    id_of_user_to_restore = request.args.get(phone_number)

    return json.dumps(UsersHandler.restore_user(id_of_user_to_restore))


# completed
@app.route('/findride', methods=['POST'])
def find_a_ride():
    logger.info('Get request to find a ride: ' + request.url)
    ride_request = create_json_object_from_request_args(request.args)

    return str(RidesHandler.find_a_ride(ride_request))


@app.route('/askforaride', methods=['POST'])
def ask_for_a_ride():
    logger.info('Get request to ask for a ride: ' + request.url)
    ride_request = create_json_object_from_request_args(request.args)

    return RidesHandler.create_ride(ride_request)


@app.route('/showmyriderequests', methods=['POST'])
def show_user_ride_requests():
    logger.info('Get request to show user ride requests: ' + request.url)
    user_id = request.args.get(phone_number)

    return RidesHandler.get_user_ride_requests(user_id)


@app.route('/cancelride', methods=['POST'])
def cancel_ride():
    logger.info('Get request to cancel ride requests: ' + request.url)
    ride_id = request.args.get(ride_ID)

    return RidesHandler.cancel_ride(ride_id)


@app.route('/acceptride', methods=['POST'])
def accept_ride():
    logger.info('Get request to accept ride requests: ' + request.url)
    ride_request = create_json_object_from_request_args(request.args)
    ride_id = request.args.get(ride_ID)

    return RidesHandler.accept_ride(ride_request, ride_id)


def add_junk_rides(i):
    ride = {
        "driverPhoneNumber": str(i),
        "driverAccepted": False,
        "passengerPhoneNumber": str(i + 1),
        "passengerAccepted": False,
        "baseLocation": "a-baseLocation",
        "wantedLocation": "a-wantedLocation",
        "date": "a-date",
        "leavingTime": "a-leavingTime"
    }

    for x in range(i + 2, i + 10):
        RidesHandler.create_ride(ride)
        ride["driverPhoneNumber"] = x
        ride["passengerPhoneNumber"] = x + 1
        x = x + 1


if __name__ == "__main__":
    logger.info('Server has reloaded')

app.run()
