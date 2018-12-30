#!/usr/bin/env python3
from gevent import monkey
monkey.patch_all()
import gevent
import os
import ssl
import asyncio

from config import config, logger, decfun
from ddbb import SQLite, es
from utils import twitterStream

import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.web import URLSpec
from tornado.options import define, options

# Tornado + jade
from tornado import template
from pyjade.ext.tornado import patch_tornado
patch_tornado()

from controller import *

_app = config.get('app',{})
BASEDIR = _app.get('basedir')

define("address", default=_app.get('listen_addr', '127.0.0.1'), type=str)
define("portHTTP", default=_app.get('port_http', '8080'), type=int)
define("portHTTPS", default=_app.get('port_https', '8443'), type=int)
define("env", default='dev', type=str)


def server_path(*args) -> str:
    fpath = BASEDIR
    for arg in args:
        fpath = os.path.join(fpath, arg)
    return fpath


class Application(tornado.web.Application):

    def __init__(self):

        # keywords = items2listen()
        keywords = ['trump']

        handlers = [
            URLSpec(r"/", GutenbergHandler, name="home"),
            #URLSpec(r"(?i)^/((\?|index|home).*?(\?.*)?)?$", HomeHandler, name="home"),

            URLSpec(r"^/wss", WebSckt),

            URLSpec(r"(?i)^/research", ResearchHandler, name="research"),
            URLSpec(r"(?i)^/gutenberg", GutenbergHandler, name="gutenberg"),
            URLSpec(r"(?i)^/imdb", ImdbHandler, name="imdb"),
            URLSpec(r"(?i)^/twitter", TwitterHandler, name="twitter", kwargs={'keywords': keywords}),
            URLSpec(r"(?i)^/charts", ChartsHandler, name="charts"),
            URLSpec(r"(?i)^/about", AboutHandler, name="about"),
            URLSpec(r"(?i)^/login", LoginHandler, name="login"),
            URLSpec(r"(?i)^/logout", LogoutHandler, name="logout"),

            URLSpec(r"(?i)^/static/js/(.*)", tornado.web.StaticFileHandler, {"path": server_path('static', 'js')}),
            URLSpec(r"(?i)^/static/css/(.*)", tornado.web.StaticFileHandler, {"path": server_path('static', 'css')}),
            URLSpec(r"(?i)^/static/img/(.*)", tornado.web.StaticFileHandler, {"path": server_path('static', 'img')}),

            URLSpec(r'(?i)^/(robots\.txt|favicon\.ico)', tornado.web.StaticFileHandler, {"path": server_path('static')}),
        ]

        settings = dict(
            debug=True,
            template_path=server_path('view'),
            static_path=server_path('static'),
            xsrf_cookies=True,
            cookie_secret=_app.get('cookie_sec'),
            default_handler_class=Error404,
            login_url="/login",
        )

        # SQLite
        self.sqlite_conn = SQLite(
            config.get('sqlite',{}).get('path'),
            config.get('sqlite',{}).get('name'),
            config.get('sqlite',{}).get('table'),
            True)

        self.sqlite_conn.create(
            config.get('sqlite',{}).get('create_tbl_twitter'))

        # Elasticsearch
        self.es_conn = es

        super(Application, self).__init__(handlers, **settings)


def resetTwitterDDBB():
    oSQLite = SQLite(config.get('sqlite',{}).get('path'),
                     config.get('sqlite',{}).get('name'),
                     config.get('sqlite',{}).get('table'),
                     True)
    oSQLite.create(config.get('sqlite',{}).get('create_tbl_twitter'))
    oSQLite.close()


def run_server():

    options.parse_command_line(final=False)

    application = Application()


    serverHTTP = tornado.httpserver.HTTPServer(application)
    serverHTTPS = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": os.path.join(BASEDIR, "config/certs/cert.crt"),
        "keyfile": os.path.join(BASEDIR, "config/certs/cert.key"),
    })
    serverHTTP.listen(options.portHTTP, address=options.address)
    serverHTTPS.listen(options.portHTTPS, address=options.address)

    logger.info('Listening on {}:{}'.format(options.address, options.portHTTP))
    logger.info('Listening on {}:{}'.format(options.address, options.portHTTPS))

    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.create_task(twitterStream(['trump', 'clinton']))
    loop.create_task(run_server())

    loop.run_forever()

    loop.close()
