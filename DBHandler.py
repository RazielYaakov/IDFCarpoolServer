import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

import log

logger = log.setup_custom_logger()

logger.info('Initialize connection with firebase-DB')
logger.info(os.environ['FIREBASE_CONFIG'])
# cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(options={
    "databaseURL": "https://carpool-832da.firebaseio.com",
    'databaseAuthVariableOverride': {
        'uid': 'IDFCarpool'
    }
})
firebase_db = db.reference()


def get_firebase_db_ref():
    return firebase_db
