# -*- coding: utf-8 -*-
import os
import sys
import uuid
import re
import tweepy
import tornado
import json
import bcrypt
from datetime import datetime
from collections import OrderedDict

from config import config, logger, decfun
from models import User, Contact
from utils import utils, es_queries

import tornado.web
import tornado.websocket
from importlib.resources import contents
from numpy.core._methods import _sum
from twisted.conch.client import direct

_app = config.get('app',{})
BASEDIR = _app.get('basedir')

class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    COOKIE_NAME = config.get('app',{}).get('cookie_name')
    COOKIE_SEC = config.get('app',{}).get('cookie_sec')
    
    @property
    def db(self):
        return self.application.db
    
    @property
    def root_path(self):
        return self.application.root_path
    
    def prepare(self):
        if 'http://' in self.request.full_url() or \
            ':8080' in self.request.headers['Host'] or \
            ('X-Forwarded-Proto' in self.request.headers and \
            self.request.headers['X-Forwarded-Proto'] != 'https'):
            
            req = re.sub(r'(?:\:\d{2,4}[/]?)+', ':8443/', self.request.full_url())
            self.redirect(re.sub(r'^([^:]+)', 'https', req))
            
        self.clear_header('Server')
        self.set_header('X-FRAME-OPTIONS', 'Deny')
        self.set_header('X-XSS-Protection', '1; mode=block')
        self.set_header('X-Content-Type-Options', 'nosniff')
        self.set_header('Strict-Transport-Security', 'max-age=31536000; includeSubdomains')
    
    def render(self, template_name, **kwargs):
        kwargs["current_url"] = self.request.uri
        self.set_secure_cookie(self.COOKIE_NAME, self.COOKIE_SEC)
        super().render(template_name, **kwargs)
    
    def get_current_user(self):
        email = self.get_secure_cookie("user")
        if email is None:
            return None
        session = self.application.session_user_db
        user = (session.query(User,Contact)
            .filter(User.id == Contact.user_id)
            .filter(Contact.email == email.decode('utf-8'))
            .first())
        return user.Contact.email
    
    def check_permission(self, action):
        user = self.get_current_user()
        admin = self.is_admin_user()
        if action in self.perm_public or (user and action in self.perm_user) or (admin and action in self.perm_admin):
            pass # ok
        else:
            self.raise403()
    
    def is_admin_user(self):
        user = self.get_current_user()
        return user and user.admin

    #def files_in_dir(self, directory):
    #    return utils.num_of_files_in_dir_rec(directory)

    def raise400(self, msg=None):
        raise tornado.web.HTTPError(400, msg or 'Invalid request')

    def raise401(self, msg=None):
        raise tornado.web.HTTPError(401, msg or 'Not enough permissions to perform this action')

    def raise403(self, msg=None):
        raise tornado.web.HTTPError(403, msg or 'Not enough permissions to perform this action')

    def raise404(self, msg=None):
        raise tornado.web.HTTPError(404, msg or 'Object not found')

    def raise422(self, msg=None):
        raise tornado.web.HTTPError(422, msg or 'Invalid request')

    def raise500(self, msg=None):
        raise tornado.web.HTTPError(500, msg or 'Something is not right')
        
        
class Error404(BaseHandler):

    def get(self):
        self.render('error404.jade', title="error")


class LoginHandler(BaseHandler):
                
    @tornado.gen.coroutine
    def get(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 3:
            self.write('<center>blocked</center>')
            return
        self.render('signin.jade', title="signin")

    @tornado.gen.coroutine
    def post(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 3:
            self.write('<center>blocked</center>')
            return
        
        form_email = tornado.escape.xhtml_escape(self.get_argument("email"))
        form_password = tornado.escape.xhtml_escape(self.get_argument("password"))
        
        if form_email and form_password:
            
            session = self.application.session_user_db
            
            user = (session.query(User,Contact)
                .filter(User.id == Contact.user_id)
                .filter(Contact.email == form_email)
                .first())
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(form_password.encode("utf-8"), salt)
            
            if user and bcrypt.hashpw(form_password.encode("utf-8"), hashed) == hashed:
                user.User.last_loggedin = datetime.now()
                user.User.no_of_logins += 1
                session.commit()
                self.set_secure_cookie("user", form_email)
                self.set_secure_cookie("incorrect", "0")
                self.redirect(self.reverse_url("home"))
                return

        incorrect = self.get_secure_cookie("incorrect") or 0
        increased = str(int(incorrect)+1)
        self.set_secure_cookie("incorrect", increased)
        self.render('signin.jade', title="signin")


class LogoutHandler(BaseHandler):
    """Logout the current user."""
    
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", self.reverse_url("home")))


class HomeHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("home.jade", title="Partners Capital")


class TwitterHandler(BaseHandler):
    
    __oSQLite = None
    __cursor = None
    
    def initialize(self, keywords):
        self.keywords = keywords
        
    def get(self, *args, **kwargs):

        col1 = 'created_at'
        col2 = 'keyword'
        col3 = 'tweet'
        col4 = 'user_name'
        col5 = 'user_followers_count'
        col6 = 'user_location'
        
        strSQL = '''
            SELECT
                strftime('%d-%m-%Y %H:%M:%S', {col1}) as Date,
                {col2} as Keyword,
                {col3} as Tweet,
                {col4} as Username,
                {col5} as Followers,
                {col6} as Location
            FROM
                {tn}
            ORDER BY Date DESC''' \
            .format(col1=col1, col2=col2, col3=col3,
                    col4=col4, col5=col5, col6=col6,
                    tn='twitter')
            
        data = self.application.sqlite_conn.select(strSQL)

        colnames = tweets = []
        if data:
            colnames = list(data[0].keys())
            tweets = [list(row.values()) for row in data]

        self.render("twitter.jade",
                    title="tweets",
                    keywords=self.keywords,
                    colnames=colnames,
                    tweets=tweets)
        

class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("about.jade", title="about")


class ProfileHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("profile.jade", title="profile")


class SectorsHandler(BaseHandler):
    
    def get(self, sector):
        if sector:
            
            folder = os.path.join(BASEDIR, 'public', 'files', sector)
            files_dir = utils.get_directory_structure(folder)
            logger.info(files_dir)
            for folder, files in files_dir.items():
                for k, v in files.items():
                    logger.info(es_queries.search_filename(k))
            self.render("sectors.jade", title="Sectors",
                        files_dir=files_dir)


class ReadOnlineHandler(BaseHandler):
    
    def get(self, folder_file):
        
        if not folder_file: raise tornado.web.HTTPError(404)
        path_img = os.path.join(BASEDIR, 'public', folder_file)
        pages = []
        if os.path.isdir(os.path.join(path_img)):
            for f in os.listdir(path_img):
                if os.path.isfile(os.path.join(path_img, f)) and f.endswith(('.jpg', '.jpeg')):
                    rel_path = os.path.join('public', folder_file, f)
                    pages.append(rel_path)
            if pages:
                pages.sort()
                self.render("readonline.jade", title="Read Online", pages=pages)
            else:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(404)


class WebSckt(tornado.websocket.WebSocketHandler):
 
    def open(self):
        logger.info("Client connected")
        self.write_message(json.dumps({
            'type': 'sys',
            'message': 'Welcome to Websocket',
            }))

    def on_close(self):
        logger.info("Client disconnected")

    def on_message(self, message):
        recv = json.loads(message)
        path = recv.get('path')
        msg = recv.get('message')
        data = {}
        
        if path and type(path) is str:    
            if path == '/':
                if msg and type(msg) is str:
                    data = es_queries.search_docs(msg)
        
            if data:
                content = {
                    'type': 'websocket',
                    'path': path, 
                    'message': data
                }
                self.write_message(json.dumps(content))

class Broadcaster(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def check_origin(self, origin):
        return True

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        self.waiters.add(self)

    def on_close(self):
        self.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, data):
        logger.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            # if waiter != self:
            try:
                waiter.write_message(data)
            except:
                logger.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logger.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        content = {
            "time": datetime.now(),
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        content["html"] = tornado.escape.to_basestring(
            self.render_string("message.jade", message=content))
        
        self.update_cache(content)
        self.send_updates(content)
