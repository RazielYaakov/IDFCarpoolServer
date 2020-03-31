import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import log

logger = log.setup_custom_logger('DBHandler')

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://carpool-832da.firebaseio.com",
    'databaseAuthVariableOverride': {
        'uid': 'IDFCarpool'
    }
})
firebase_db = db.reference()


def get_firebase_db_ref():
    return firebase_db
