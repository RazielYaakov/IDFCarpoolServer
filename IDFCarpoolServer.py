from datetime import datetime

from flask import Flask, request

import DBHandler
import RidesAsker
import RidesFounder
import log
from consts import phone_number, user_type, driver_type, leaving_time, destination, source

app = Flask(__name__)
logger = log.setup_custom_logger('IDFCarpoolService')


def create_json_object_from_request_args(request_args):
    return {argument: request_args.get(argument) for argument in request_args}


@app.route('/')
def hello():
    return 'Raziel Yaakov'


@app.route('/createuser', methods=['POST'])
def create_new_user():
    logger.info('Get request to create new user: ' + request.url)
    new_user_data = create_json_object_from_request_args(request.args)

    return DBHandler.create_new_user(new_user_data)


@app.route('/updateuser', methods=['POST'])
def update_user():
    logger.info('Get request to update user: ' + request.url)
    updated_user_data = create_json_object_from_request_args(request.args)

    return DBHandler.update_user(updated_user_data)


@app.route('/deleteuser', methods=['POST'])
def delete_user():
    logger.info('Get request to delete user: ' + request.url)
    id_of_user_to_delete = request.args.get(phone_number)

    return DBHandler.delete_user(id_of_user_to_delete)


@app.route('/findaride', methods=['POST'])
def find_a_ride():
    logger.info('Get request to find a ride: ' + request.url)
    ride_request = create_json_object_from_request_args(request.args)

    return RidesFounder.find_a_ride(ride_request)


@app.route('/askforride', methods=['POST'])
def ask_for_a_ride():
    logger.info('Get request to ask for a ride: ' + request.url)
    ride_request = create_json_object_from_request_args(request.args)

    return RidesAsker.ask_for_a_ride(ride_request)


# def add_junk_drivers(index):
#     junk_driver_template = {
#         'name': 'Razi',
#         'destination': 'a',
#         'phoneNumber': '1',
#         'userType': driver_type,
#         'leavingTime': '6',
#         'source': 'b'
#     }
#
#     for i in range(index, index + 50):
#         DBHandler.create_new_user(junk_driver_template)
#         junk_driver_template[phone_number] = i
#         if i % 2 == 0:
#             junk_driver_template[leaving_time] = '5'
#             junk_driver_template[destination] = 'b'
#             junk_driver_template[source] = 'a'
#         else:
#             junk_driver_template[leaving_time] = '6'
#             junk_driver_template[destination] = 'a'
#             junk_driver_template[source] = 'b'
#
#
# def get_all_drivers():
#     drivers = DBHandler.get_all_users_with_specific_routes_and_hour('a', 'b', '5')
#
#     for driver in drivers:
#         print(str(driver))


if __name__ == "__main__":
    logger.info('Server has reloaded')
    app.run(debug=True)

