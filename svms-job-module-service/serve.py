import sys
import os
sys.path.append(os.getcwd())

from decouple import config
from aiohttp import web
from urls import url_mapper

app = web.Application()
app.add_routes(url_mapper())
web.run_app(app,
                host=config('APP_HOST'), 
                port=config('APP_PORT'))