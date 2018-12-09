#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import ssl
import logging
import asyncio
import threading

from config import conf_app, conf_sqlite, conf_es
from ddbb import SQLite, es
from utils import OpenStream

import tweepy

import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.web import URLSpec
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.options import define, options

# Tornado + jade
from tornado import template
from pyjade.ext.tornado import patch_tornado
patch_tornado()

from controller import *

BASEDIR = conf_app.get('BASEDIR')

logging.getLogger().setLevel(logging.DEBUG)

define("address", default=conf_app.get('LISTEN_ADDR'), type=str)
define("portHTTP", default=conf_app.get('PORT_HTTP'), type=int)
define("portHTTPS", default=conf_app.get('PORT_HTTPS'), type=int)
define("env", default='dev', type=str)

def server_path(*args) -> str:
    fpath = BASEDIR
    for arg in args:
        fpath = os.path.join(fpath, arg)
    return fpath

class Application(tornado.web.Application):

    def __init__(self, handlers, **kwargs):
                
        settings = dict(
            debug = True,
            template_path = server_path('view'),
            static_path = server_path('static'),
            xsrf_cookies = conf_app.get('XSRF'),
            cookie_secret = conf_app.get('COOKIE_SEC'),
            default_handler_class = Error404
        )
        
        # SQLite
        self.sqlite_conn = SQLite(conf_sqlite.get('path'),
                                conf_sqlite.get('name'),
                                conf_sqlite.get('table'),
                                kwargs.get('deleteTable', False))
        if kwargs.get('deleteTable', False):
            self.sqlite_conn.create(conf_sqlite.get('create_tbl_twitter'))
        
        # Elasticsearch
        self.es_conn = es

        tornado.web.Application.__init__(self, handlers, **settings)



def resetTwitterDDBB():
    oSQLite = SQLite(conf_sqlite.get('path'),
                     conf_sqlite.get('name'),
                     conf_sqlite.get('table'),
                     True)
    oSQLite.create(conf_sqlite.get('create_tbl_twitter'))
    oSQLite.close()


def main():

    # keywords = items2listen()
    keywords = ['trump']

    router = [
        URLSpec(r"/", HomeHandler, name="index"),

        URLSpec(r"/wss", WebSckt),
        URLSpec(r"/wssbcst", Broadcaster),

        URLSpec(r"/(?i)home", HomeHandler, name="home"),
        URLSpec(r"/(?i)tweets", TweetsHandler, name="tweets", kwargs={'keywords':keywords}),
        URLSpec(r"/(?i)search", SearchHandler, name="search"),
        URLSpec(r"/(?i)charts", ChartsHandler, name="charts"),
        URLSpec(r"/(?i)about", AboutHandler, name="about"),

        URLSpec(r"/(?i)static/js/(.*)", tornado.web.StaticFileHandler, {"path": server_path('static', 'js')}),
        URLSpec(r"/(?i)static/css/(.*)", tornado.web.StaticFileHandler, {"path": server_path('static', 'css')}),
        URLSpec(r"/(?i)static/img/(.*)", tornado.web.StaticFileHandler, {"path": server_path('static', 'img')}),

        URLSpec(r'/(?i)(robots\.txt|favicon\.ico)', tornado.web.StaticFileHandler, {"path": server_path('static')}),
    ]

    options.parse_command_line(final=False)

    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

    #threading.Thread(target=OpenStream, args=(keywords,)).start()

    application = Application(handlers=router, deleteTable=True)

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

    logging.info('Listening on {}:{}'.format(options.address, options.portHTTP))
    logging.info('Listening on {}:{}'.format(options.address, options.portHTTPS))

    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
