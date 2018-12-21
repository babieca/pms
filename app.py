#!/usr/bin/env python3
import os
import ssl
import asyncio

from config import conf, logger, decfun
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

BASEDIR = conf.get('app',{}).get('basedir')

define("address", default=conf.get('app',{}).get('listen_addr'), type=str)
define("portHTTP", default=conf.get('app',{}).get('port_http'), type=int)
define("portHTTPS", default=conf.get('app',{}).get('port_https'), type=int)
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
            URLSpec(r"(?i)^/((\?|index|home).*?(\?.*)?)?$", HomeHandler, name="index"),

            URLSpec(r"^/wss", WebSckt),

            URLSpec(r"(?i)^/home", HomeHandler, name="home"),
            URLSpec(r"(?i)^/tweets", TweetsHandler, name="tweets", kwargs={'keywords': keywords}),
            URLSpec(r"(?i)^/search", SearchHandler, name="search"),
            URLSpec(r"(?i)^/charts", ChartsHandler, name="charts"),
            URLSpec(r"(?i)^/about", AboutHandler, name="about"),

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
            cookie_secret=conf.get('app',{}).get('cookie_sec'),
            default_handler_class=Error404
        )

        # SQLite
        self.sqlite_conn = SQLite(
            conf.get('sqlite',{}).get('path'),
            conf.get('sqlite',{}).get('name'),
            conf.get('sqlite',{}).get('table'),
            True)

        self.sqlite_conn.create(
            conf.get('sqlite',{}).get('create_tbl_twitter'))

        # Elasticsearch
        self.es_conn = es

        super(Application, self).__init__(handlers, **settings)


def resetTwitterDDBB():
    oSQLite = SQLite(conf.get('sqlite',{}).get('path'),
                     conf.get('sqlite',{}).get('name'),
                     conf.get('sqlite',{}).get('table'),
                     True)
    oSQLite.create(conf.get('sqlite',{}).get('create_tbl_twitter'))
    oSQLite.close()


def run_server():

    options.parse_command_line(final=False)

    application = Application()

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(os.path.join(BASEDIR, "config/certs/cert.crt"),
                            os.path.join(BASEDIR, "config/certs/cert.key"))

    # server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx)
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
