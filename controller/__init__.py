# -*- coding: utf-8 -*-
import os
import uuid
import datetime
import re
import tweepy
import tornado
import json
from config import conf, logger, decfun

from collections import OrderedDict

import tornado.web
import tornado.websocket


class BaseController(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    COOKIE_NAME = conf.get('app',{}).get('cookie_name')
    COOKIE_SEC = conf.get('app',{}).get('cookie_sec')
    
    @property
    def db(self):
        return self.application.db
    
    @property
    def root_path(self):
        return self.application.root_path
    
    def prepare(self):
        # print(self.request.full_url())
        # print(self.request.headers)
        # print('='*100)
        if ('http://' in self.request.full_url() or
            ':8080' in self.request.headers['Host'] or
            (('X-Forwarded-Proto' in self.request.headers and 
            self.request.headers['X-Forwarded-Proto'] != 'https'))):
            req = re.sub(r'(?:\:\d{2,4}[/]?)+', ':8443/', self.request.full_url())
            self.redirect(re.sub(r'^([^:]+)', 'https', req))
    
    def render(self, template_name, **kwargs):
        kwargs["current_url"] = self.request.uri
        self.set_secure_cookie(self.COOKIE_NAME, self.COOKIE_SEC)
        super().render(template_name, **kwargs)
    
    def get_current_user(self):
        user = None
        try:
            user_json = self.get_secure_cookie("user")
            if not user_json: return None
            user = json.loads(user_json, object_hook=datetime_decoder)
            if user:
                user = User(raw_data=user)
                user.validate()
        except Exception as err:
            logger.fatal("[{0}] {1}".format(sys._getframe().f_code.co_name, err))
        return user
        
        
class Error404(BaseController):

    def get(self):
        self.render('error404.jade', title="error")


class HomeHandler(BaseController):

    def get(self, *args, **kwargs):
        self.render("forms.jade", title="home")


class TweetsHandler(BaseController):
    
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

        self.render("tweets.jade",
                    title="tweets",
                    keywords=self.keywords,
                    colnames=colnames,
                    tweets=tweets)

        
class SearchHandler(BaseController):

    doc = {
            '_source': ['title', 'film_rating', 'duration', 'genre', 'release_date'],
            'query': {
                'match_all' : {}
           },
            'size' : 50,
            'from': 0,
       }

    def initialize(self):
        data = {}
        self.res = self.application.es_conn.search(index='imdb', doc_type='doc', body=self.doc, scroll='1m')
        #scrollId = self.res['_scroll_id']    
        #es.scroll(scroll_id = scrollId, scroll = '1m')
    
    def get(self):
        
        all_keys = set()
        content = []
        for row in self.res['hits']['hits']:
            all_keys |= set(row['_source'].keys())
            content.append(row['_source'])
        
   
        self.render("search.jade",
                    title =" search",
                    colnames = all_keys,
                    data = content,
                    message=False)
        
        
class ChartsHandler(BaseController):

    def get(self, *args, **kwargs):
        self.render("charts.jade", title="charts")


class AboutHandler(BaseController):

    def get(self, *args, **kwargs):
        self.render("about.jade", title="about")


class WebSckt(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True
 
    def open(self):
        self.write_message(json.dumps({
            'type': 'sys',
            'message': 'Welcome to Websocket',
            }))
        logger.info("Client connected")

    def on_close(self):
        logger.info("Client disconnected")

    def on_message(self, message): #, message):
        logger.info("message: {}".format(message))
        #self.write_message(message)
        self.write_message(json.dumps({
                'type': 'user',
                'id': id(self),
                'message': message,
            }))

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
            "time": datetime.datetime.now(),
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        content["html"] = tornado.escape.to_basestring(
            self.render_string("message.jade", message=content))
        
        self.update_cache(content)
        self.send_updates(content)


__all__ = ['HomeHandler',
           'WebSckt',
           'TweetsHandler',
           'ChartsHandler',
           'SearchHandler',
           'AboutHandler',
           'Error404']
