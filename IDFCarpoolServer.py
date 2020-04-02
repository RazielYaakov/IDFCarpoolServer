from flask import Flask, request

import RidesHandler
import UsersHandler
import log
from consts import phone_number, ride_ID, user_type

app = Flask(__name__)
logger = log.setup_custom_logger()


def create_json_object_from_request_args(request_args):
    return {argument: request_args.get(argument) for argument in request_args}


@app.route('/')
def hello():
    return 'Raziel Yaakov'


# completed
@app.route('/login', methods=['POST'])
def login_user():
    logger.info('Get request to login: ' + request.url)
    user_data = create_json_object_from_request_args(request.args)

    return UsersHandler.login(user_data)


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
@app.route('/findride', methods=['POST'])
def find_ride():
    logger.info('Get request to find ride: ' + request.url)
    find_ride_request = create_json_object_from_request_args(request.args)

    return str(RidesHandler.find_ride(find_ride_request))


@app.route('/showmyriderequests')
def show_user_ride_requests():
    logger.info('Get request to show user ride requests: ' + request.url)
    type_of_user = request.args.get(user_type)
    user_id = request.args.get(phone_number)

    return str(RidesHandler.get_user_ride_requests(type_of_user, user_id))


@app.route('/cancelride', methods=['POST'])
def cancel_ride():
    logger.info('Get request to cancel ride requests: ' + request.url)
    type_of_user = request.args.get(user_type)
    ride_id = request.args.get(ride_ID)

    return RidesHandler.cancel_ride(type_of_user, ride_id)


@app.route('/acceptride', methods=['POST'])
def accept_ride():
    logger.info('Get request to accept ride requests: ' + request.url)
    type_of_user = request.args.get(user_type)
    ride_id = request.args.get(ride_ID)

    return RidesHandler.accept_ride(type_of_user, ride_id)


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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    logger.info('Server has reloaded')
    logger.info('Queen Dana Koren')


