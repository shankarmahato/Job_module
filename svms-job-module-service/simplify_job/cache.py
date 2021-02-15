from django.conf import settings
import json
from django.core.cache import cache
from json import JSONEncoder
from uuid import UUID
from simplify_job.apps import ValidateHandeler

logger = settings.LOGGER

# override default JSON encoder
JSONEncoder_default = JSONEncoder.default

def JSONEncoder_override_default(self, o):
    if isinstance(o, UUID):
        return str(o)
    return JSONEncoder_default(self, o)

JSONEncoder.default = JSONEncoder_override_default
 
logger = settings.LOGGER

class RedisCacheHandler:
    @staticmethod
    def set(key, payload, json_encode=True):
        key = '{}'.format(key)
        try:
            if json_encode is True:
                payload = json.dumps(payload)
            logger.info('setting cache data of key: {}, data: {}'.format(key, payload))
            settings.REDIS_STORE.set(key, payload,ex=600) 
        except Exception as e:
            logger.error("Unable to SET CACHE error -- {}, data -- {}".format(e,payload))
 
    @staticmethod
    def get(key, json_decode=True):
        data = settings.REDIS_STORE.get(key)
        try:
            if json_decode is True and data is not None:
                data = json.loads(data)
                logger.info('getting cache data of key: {}: data: {}'.format( key, data))
        except Exception as e:
            logger.error("Unable to GET CACHE  -- {}, data -- {}".format(e,data))
            data = []
        return data
 

    @staticmethod
    def purge(key):

        # settings.TTLCACHE.clear()
        '''Remove all cached keys containing uuids present in cache_key'''
        if key == "*":
            cache.clear()
        else:
            settings.REDIS_STORE.delete(key)

            
    @staticmethod
    def purge_related(key):
        # settings.TTLCACHE.clear()
        '''Remove all cached keys containing uuids present in cache_key'''
        key_pieces = key.split(':')
        for key_piece in key_pieces:
            valid_uuid = ValidateHandeler.is_valid_uuid(key_piece)
            if valid_uuid is not None:
                cache.delete_pattern(f'*{valid_uuid}*')