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

from controller import BaseHandler
from config import config, logger, decfun
from models import User, Contact, Tweets
from utils import utils, es_queries

import tornado.web
import tornado.websocket
from importlib.resources import contents
from numpy.core._methods import _sum
from twisted.conch.client import direct

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
                self.redirect(self.reverse_url("search"))
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


class SearchHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("search.jade", title="Partners Capital")


class TwitterHandler(BaseHandler):
        
    def get(self, *args, **kwargs):
        session = self.application.session_twitter_db
        result = (session.query(Tweets).with_entities(
            Tweets.created_at,
            Tweets.keyword,
            Tweets.tweet,
            Tweets.user_name,
            Tweets.user_followers_count,
            Tweets.user_location).order_by(Tweets.created_at.desc()).all())

        self.render("twitter.jade",
                    title="tweets",
                    keywords="trump",
                    colnames=["Created at", "Keyword", "Tweet", "Username",
                              "Followers", "User location"],
                    tweets=result)
        

class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("about.jade", title="about")


class ProfileHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("profile.jade", title="profile")


class SectorsHandler(BaseHandler):
    
    def get(self, sector):
        if sector:
            docs = {}
            folder = os.path.join(self.application.basedir, 'public', 'files', sector)
            files_dir = utils.get_directory_structure(folder)

            for folder, files in files_dir.items():
                for filename, _ in files.items():
                    dot = filename.find('.')
                    res = es_queries.search_by_filename_and_folder(
                        filename[:dot], os.path.join('files', sector))
                    docs = {**docs, **res}
            self.render("sectors.jade", title="Sectors",
                        docs=docs)


class ReadOnlineHandler(BaseHandler):
    
    def get(self, folder_file):
        
        if not folder_file: raise tornado.web.HTTPError(404)
        path_img = os.path.join(self.application.basedir, 'public', folder_file)
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
                    data = es_queries.search_docs( should=msg, must='', must_not= '')
                elif msg:
                    data = es_queries.search_docs(
                        should=msg.get('should',''),
                        must=msg.get('must', ''),
                        must_not=msg.get('must_not',''),
                        sector=msg.get('sector', ''),
                        date_from=msg.get('from', ''),
                        date_to=msg.get('to', ''))
        
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
