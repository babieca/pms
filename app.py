#!/usr/bin/env python3
from gevent import monkey
monkey.patch_all()
import gevent
import os
import ssl
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config

from config import config, logger, decfun
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


# sqlalchemy - User
db_path_user = config.get('users',{}).get('db', {}).get('path')
db_url_user = 'sqlite:///{db}'.format(db=db_path_user)
engine_user = create_engine(db_url_user)

# sqlalchemy - Twitter
db_path_twitter = config.get('twitter',{}).get('db', {}).get('path')
db_url_twitter = 'sqlite:///{db}'.format(db=db_path_twitter)
engine_twitter = create_engine(db_url_twitter)

Session1 = sessionmaker()
Session1.configure(bind=engine_user)
session_user = Session1()

Session2 = sessionmaker()
Session2.configure(bind=engine_twitter)
session_twitter = Session2()


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
        handlers = [
            #URLSpec(r"/", SearchHandler, name="search"),
            URLSpec(r"(?i)^/((\?|index|home|search).*?(\?.*)?)?$", SearchHandler, name="search"),

            URLSpec(r"^/wss", WebSckt),
            URLSpec(r"^/bcst", Broadcaster),

            URLSpec(r"(?i)^/twitter", TwitterHandler, name="twitter"),
            URLSpec(r"(?i)^/about", AboutHandler, name="about"),
            URLSpec(r"(?i)^/sectors/(.*)", SectorsHandler, name="sectors"),
            
            URLSpec(r"(?i)^/login", LoginHandler, name="login"),
            URLSpec(r"(?i)^/logout", LogoutHandler, name="logout"),
            URLSpec(r"(?i)^/profile", ProfileHandler, name="profile"),
            
            URLSpec(r"(?i)^/readonline/(.*)", ReadOnlineHandler, name="readonline"),
            
            URLSpec(r"(?i)^/public/(.*)", tornado.web.StaticFileHandler, {"path": server_path('public')}),
            
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

        
        # User db
        self.session_user_db = session_user
        self.session_twitter_db = session_twitter

        self.basedir = BASEDIR
        self.cookie_name = config.get('app',{}).get('cookie_name')
        self.cookie_sec = config.get('app',{}).get('cookie_sec')
        
        super(Application, self).__init__(handlers, **settings)


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
    loop.create_task(twitterStream(keywords=['trump', 'brexit'], session_db=session_twitter))
    loop.create_task(run_server())
    loop.run_forever()
    loop.close()
