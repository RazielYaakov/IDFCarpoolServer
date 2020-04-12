import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

import log

logger = log.setup_custom_logger()

logger.info('Initialize connection with Firebase-DB')
c = {
    "type": "service_account",
    "project_id": "carpool-832da",
    "private_key_id": str(os.environ['PRIVATE_KEY_ID']),
    "private_key": str(os.environ['PRIVATE_KEY']),
    "client_email": "firebase-adminsdk-q1v82@carpool-832da.iam.gserviceaccount.com",
    "client_id": "115695783675345850330",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-q1v82%40carpool-832da.iam.gserviceaccount.com"
}

cred = credentials.Certificate(c)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://carpool-832da.firebaseio.com",
    'databaseAuthVariableOverride': {
        'uid': 'IDFCarpool'
    }
})
firebase_db = db.reference()


def get_firebase_db_ref():
    return firebase_db
