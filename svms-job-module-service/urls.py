# from app.views import IndexViewset
from aiohttp import web
from django.conf import settings
from app.views import IndexViewset, PingViewset


def url_mapper():
    mapper = []
    mapper.append(web.get(settings.VMS_JOB_MODULE, IndexViewset))
    mapper.append(web.get(settings.VMS_JOB_MODULE_PING, PingViewset))
    mapper.append(web.get(settings.VMS_JOB_MODULE_JOBS, IndexViewset))
    return mapper
