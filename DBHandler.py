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
  "private_key_id": "6749d94b1fb4341e66a9cda4d85dad3cac0f9af8",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDN449IYBaTp4su\nR7c9S3AQ5xWg5Yb4io7v3+DVmoxNUvlYQ240tBe3hHtrbNr+RZgnqyXso7DjqttS\npEDvSUfjg8wwo7cToEv5sJLD/ZQKKI2ZG+Clag1u2ULWdCacPo3pYTSwvbcCcM4W\n9xXyUmCYHCJNNwsehtckSa+FKtZ6ytFG615HxSe6aZbZ5WQ2V3W1usA8cbgmNYHs\n6KbV+i7SKnwGEaiqvF1EMPeWUWnBGZSsMT6TaL6ysisNb2dp3Imi65YD/Bv73r89\nDwx/FRtn3Bx7vg9jbGYEVXMwHIzS44A10mgUh4RU0lK7HDqpFkXUWwDOzE++klcp\ntgJvQxErAgMBAAECggEANGWJtOMTS89zObtxlC1LH1oX5IMVRtJITx6cIvA6bYFE\nyKQce1grwv35xNyGnPhMIShKtf7wiPgV6eG4Ts1I+Ms1X1mCwYFlZG195Ff34V/x\nrTntgVtMgN3Uxyv3GYNH7VFaLfKSDRJ1OF34XVt+jqd2SU1NTJ8HSIpiG1NMEyJu\nnsiWg+RL1FtvRBdOe78TLHt4DEqyJTBz3ifeThAsS6tfnbCy5fWRdMd1nO7UEn/Q\nAmk+jdqQlLcW5tRk56ATVjmpFb1/PB2QBV/EG0Hsk0Ag6IXHWG3EgIFrXDdUqMlY\n9WTP0Qrcz/zayY+hnnuUE7LZ5zugr4gtoI7bE255QQKBgQDq1LO8G1yG/dJGLJxr\n5PdEmYFQm1MTfEAcmP1Cw+8r7/7jW6KYBGlJaIV+klL+0RrN+iS1P5w7K0INE3pJ\nnI6u0lqAIpqLYU9l3/IbrOOqLBZhhLgldagVJyhwjDdw/TSFZDoQugzI6qbjj1Lr\nTK190h/P5sSeoW4+fgg5c3knawKBgQDgcvNs1+RKzWjd6z+NW1oNrQxyhr8G5mD6\nDxcqyecO446KOpxd1oGAkgimrksCeWEOax3recVO8kfLD9FXe8z6AdRo2ARTvipR\ntpIlkWGOgGUkx4HQUsMgnCCmD13O7R0i8fw28Dj2okSgJrzd5g6YwoqNUHj4L3ZV\nnFCNdobtQQKBgBfRQPWINOdAIS6a4baTv3yGsTXyuwdT59C+t5ko9D4ZllmK9r/C\nWsdmQXvn7WEI5lYT09tKO1dI+OcInbOPnG0gyqsKV3Bhi0MC5rRl4aVl2VNEucSa\n3VRf51sa7ZiZJdWNp9IAfMF4Azs7UyaoXURQpodYmYKZTuwprj3dd2FHAoGBAIWf\nyg6txWtHOTyNdquIjGeB89wnHolUFL4qx8cgpt/1WAIxfLBdKYJK7r2VHHEfpEm6\nOfjb6Tzj/xwEkcQ8nz7kYfn9SS42E+nMANw+3k7BX/XylPVaoHLEoKdclKPCBMuu\nN1LZ13/2AVc7WMve0CfgAi65jxtq3k9/nXFq9E9BAoGAInc7pOOI4WxueKRTCPXp\n6xsk6mxGZbhL1S2REmpYQpHZk2g3I3oYgvWlgYT5uE/3NLDtMG9LK1Eq9WkWpMLs\nO5NXJ5wh7F4aklLTnmgdQvM7Au9aN/YvxNFoCxePuADoN1uYS5jhSFsbKBq8YiyT\nlKk1D5wkjKyom+QO6+vElgA=\n-----END PRIVATE KEY-----\n",
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
