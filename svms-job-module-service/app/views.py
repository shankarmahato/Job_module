# from moaiohttp.library.views import APIViewset
from aiohttp import web
from decouple import config
import json

class APIViewset(web.View):
    async def get(self):
        return self.sendResponse({
            'error': {
                'message': 'GET method not implemented for the current resource'
            }
        })

    async def post(self):
        return self.sendResponse({
            'error': {
                'message': 'POST method not implemented for the current resource'
            }
        })

    async def patch(self):
        return self.sendResponse({
            'error': {
                'message': 'PATCH method not implemented for the current resource'
            }
        })

    async def put(self):
        return self.sendResponse({
            'error': {
                'message': 'PUT method not implemented for the current resource'
            }
        })

    async def delete(self):
        return self.sendResponse({
            'error': {
                'message': 'DELETE method not implemented for the current resource'
            }
        })
    
    def sendResponse(self, payload, statusCode=200):
        return web.Response(body=json.dumps(payload),
                                status=statusCode, 
                                content_type='application/json')


class IndexViewset(APIViewset):
    pass


class PingViewset(APIViewset):
    async def get(self):
        return self.sendResponse({
            'version': config('APP_VERSION'),
            'message': 'PONG'
        })