import asyncio
import logging
import os

import motor.motor_asyncio
from rest_tools.utils.json_util import json_decode
from rest_tools.server import (RestServer, RestHandler, RestHandlerSetup,
                               from_environment, catch_error, authenticated)
from tornado.web import RequestHandler, HTTPError


class APITest(RestHandler):
    def initialize(self, db=None, **kwargs):
        super().initialize(**kwargs)
        self.db = db

    @catch_error
    async def get(self):
        search_id = self.get_argument('search_id', 'default')
        ret = await self.db.tests.find_one({'id': search_id}, projection={'_id': False})
        if not ret:
            raise HTTPError(404, reason='id not found')
        self.write(ret)  # return json document

    @authenticated
    async def post(self):
        incoming_data = json_decode(self.request.body)
        # do various checks/filters on data
        await self.db.tests.insert_one(incoming_data)
        self.write({})  # indicate success


class Web(RequestHandler):
    def initialize(self, db=None, debug=False, **kwargs):
        self.db = db
        self.debug = debug

    async def get(self, *args):
        ret = await self.db.tests.find({}, projection={'_id': False}).to_list(10000)
        self.render('index.html', tests=ret)


def create_server():
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    default_config = {
        'HOST': 'localhost',
        'PORT': 8080,
        'DEBUG': False,
        'AUTH_SECRET': 'secret',
        'DB_URL': 'mongodb://localhost/db_name',
    }
    config = from_environment(default_config)


    rest_config = {
        'debug': config['DEBUG'],
        'auth': {
            'secret': config['AUTH_SECRET'],
        }
    }

    kwargs = RestHandlerSetup(rest_config)

    logging.info(f'DB: {config["DB_URL"]}')
    db_url, db_name = config['DB_URL'].rsplit('/', 1)
    db = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    logging.info(f'DB name: {db_name}')
    kwargs['db'] = db[db_name]

    server = RestServer(static_path=static_path, template_path=static_path, debug=config['DEBUG'])


    server.add_route('/api/test', APITest, kwargs)
    server.add_route('/', Web, kwargs)

    server.startup(address=config['HOST'], port=config['PORT'])

    return server


if __name__ == '__main__':
    # handle logging
    setlevel = {
        'CRITICAL': logging.CRITICAL,  # execution cannot continue
        'FATAL': logging.CRITICAL,
        'ERROR': logging.ERROR,  # something is wrong, but try to continue
        'WARNING': logging.WARNING,  # non-ideal behavior, important event
        'WARN': logging.WARNING,
        'INFO': logging.INFO,  # initial debug information
        'DEBUG': logging.DEBUG  # the things no one wants to see
    }

    default_config = {
        'LOG_LEVEL': 'INFO',
    }
    config = from_environment(default_config)
    if config['LOG_LEVEL'].upper() not in setlevel:
        raise Exception('LOG_LEVEL is not a proper log level')
    logformat = '%(asctime)s %(levelname)s %(name)s %(module)s:%(lineno)s - %(message)s'
    logging.basicConfig(format=logformat, level=setlevel[config['LOG_LEVEL'].upper()])

    # start server
    create_server()
    asyncio.get_event_loop().run_forever()
