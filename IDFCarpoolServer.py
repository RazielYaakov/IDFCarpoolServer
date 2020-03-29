from flask import Flask, request

import DBHandler
import RidesAsker
import RidesFounder
import log
from consts import phone_number, user_type

app = Flask(__name__)
logger = log.setup_custom_logger('IDFCarpoolService')


def create_json_object_from_request_args(request_args):
    return {argument: request_args.get(argument) for argument in request_args}


@app.route('/')
def hello():
    logger.info('Get request to create new user')
    return 'Raziel Yaakov'


@app.route('/createuser', methods=['POST'])
def create_new_user():
    logger.info('Get request to create new user')

    if request.method == 'POST':
        user_data = create_json_object_from_request_args(request.args)

        return DBHandler.create_new_user(request.args.get(user_type), user_data)


@app.route('/updateuser', methods=['POST'])
def update_user():
    logger.info('Get request to update user')

    if request.method == 'POST':
        user_data = create_json_object_from_request_args(request.args)

        return DBHandler.update_user(request.args.get(user_type), user_data)


@app.route('/deleteuser', methods=['POST'])
def delete_user():
    logger.info('Get request to delete user')
    user_id = request.args.get(phone_number)

    return DBHandler.delete_user(request.args.get(user_type), user_id)


@app.route('/findaride', methods=['POST'])
def delete_user():
    logger.info('Get request to find a ride')
    ride_request = create_json_object_from_request_args(request.args)

    return RidesFounder.find_a_ride(ride_request)


@app.route('/askforride', methods=['POST'])
def delete_user():
    logger.info('Get request to ask for a ride')
    ride_request = create_json_object_from_request_args(request.args)

    return RidesAsker.ask_for_a_ride(ride_request)


if __name__ == "__main__":
    logger.info('Server has reloaded')
    app.run()
