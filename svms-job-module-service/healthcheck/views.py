from django.http import HttpResponse
import json
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
import redis


def check_mysql_db_connection():
    db_conn = connections['default']

    try:
        db_conn.cursor()
        db_conn.close()
    except OperationalError:
        connected = False
    else:
        connected = True

    return connected


def check_redis_connection():

    try:
        settings.REDIS_STORE.ping()
    except (redis.exceptions.ConnectionError,
            redis.exceptions.BusyLoadingError):
        return False
    return True


def ping(request, *args, **kwargs):

    response_data = {
        "database:mysql": check_mysql_db_connection(),
        "caching:redis": check_redis_connection(),
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")
