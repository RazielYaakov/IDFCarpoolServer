import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import log

logger = log.setup_custom_logger()

logger.info('Initialize connection with firebase-DB')
c = {
    "type": "service_account",
    "project_id": "carpool-832da",
    "private_key_id": "1667117e345425b2b0644339c5cf1c021bcb277f",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC5q6WsUDd8vTVT\na/C67nyR+sGQSWkflvPw3iPimvZeQswgUf5v+gPEBwmAVSw/pwtCBD4Uv26pZ2fe\nkgFl2eLEHshk9ngTLW3FuH/z1ZIbsar1bxG8Y+vleCrbZNRt3BMRkAaUNhSCnOp3\n9kiOUJnKKp+EKOFiTp6WMCJN4eaigKHw7WSeVshL9IWAb9mKjB0LvtEY15i69wKS\nJgm04582hJGOpQgYaU5VvT7Lv5/qfnt7l89MRbVWcgR7xp+QYj95e1m4Op+LygFo\nuiu7fjsjrNVxicsd0qw2cGi5RGw5+096bZM+F5vFpm9J5nCcauufJembJ0kIcdTw\nsG6wEQNPAgMBAAECggEAGZTGK0MUGgohnkBJdx/jpuNDJwOOSc1tB7s7e325Qwx1\n/l/9q+To/umvS/CwO4bi3LIj8YzcjNeT7oz0R1mpTjclig+RRKcmMC825dv/mPQ2\nJ0Gp0mh7+G5BjV/LiuVe9TUASwxWcBZ5kZSrs3v0bG/J8ZYGU5qca/nuyAc/VRUi\neZZplZLF2QnUiGzoP/ato9MXCErJ0gKIvCkwd+KOVVFcNbUJ+NIJziyxiE6zGYhF\nGDfNJKHuW/NTQ3DDV9F45HOzyEEBtRQ+s5r6BqRnuiUmGYcVGjfaUMR745mX7KjT\nZL2QxGNY670eytEk1tmk2dKIb8MUs//oFcQ4O0KkFQKBgQD1pHLQyHwlLefLyH6W\nQUe1eZG/tkCbZ8KVLQL/FmnYlXoQJK/7A9oWW579j7t+oUcVPbvNfCLboytqmGSk\nqQRB51DMXHzqwaSpNYVhLxY9oS9qCqzloIfBjzhvmC+hizrxyHuzxEFh82i0p/61\nIR9culburqiW4jV2rbsItefNywKBgQDBf9c9UjU1VNzAr41VPILU6JW+6fWNhstk\nZvB5D21sMPnnqWafR2S3VxU0bwcx0pGqwN/sbHbbLYz2qTgGpzaBS1PIZtF7hGNp\nhuxVzsdweUPYR+I5DAeUsCBv3Oy3VvfR7zaujoQY0VGLvaYi/kBTRYEwwUXEXOiZ\n7CM6h3CwDQKBgQCPqasA0pBQykVL2Km4RNuklkIYpoWongmeZ2HeQISNB/cIo/xM\nSVduRg15bGuSxs4k7SL+LcDRRd/pitEpwDPeO2P08Y6ZWcFsuQGV8g0G5FMvqKiv\n77AWEyZFlfMdfqltqPw4CerXV52AMtRzqLiH6e9XzsyI2im8jCTcFk9I+wKBgQCn\nhGax5ta7qhFHG3RPA4j8i7MASgnUkYrKDDhJhiqkDK59eXGnmSY/dzubXjerUXHc\nkwgI5UnsrD2qWYtwbxjHzI/nIeRfe5iZBj7adp7A56rttiXKX3i8p9IdJfUlMDxx\n2hfL/QOtfKGNSg1npBfKP5T9wYUF361bfExvYkwTjQKBgQDi8EqlpgmIc7HPIUvN\nMxUmAsYMDBw80i/+mVLiRKNCcPsQHI5mLM1rNFpP5JnHI03n0ymaxFqHdqWbEN35\nBU7I7CGG//wWePzfFq7JKAmIGO0cT04w7ue2EL2TYPnGUzkrLaAi2hn/RQA+tB3f\nw61JzoOAbAEUwxokw992ixsmnQ==\n-----END PRIVATE KEY-----\n",
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
