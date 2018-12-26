# -*- coding: utf-8 -*-
import os
import sys
import uuid
import datetime
import re
import tweepy
import tornado
import json
from config import config, logger, decfun

from collections import OrderedDict

import tornado.web
import tornado.websocket
from importlib.resources import contents


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
    
    def render(self, template_name, **kwargs):
        kwargs["current_url"] = self.request.uri
        self.set_secure_cookie(self.COOKIE_NAME, self.COOKIE_SEC)
        super().render(template_name, **kwargs)
    
    def get_current_user(self):
        return self.get_secure_cookie("user")


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
        
        getusername = tornado.escape.xhtml_escape(self.get_argument("username"))
        getpassword = tornado.escape.xhtml_escape(self.get_argument("password"))
        if "demo" == getusername and "demo" == getpassword:
            self.set_secure_cookie("user", self.get_argument("username"))
            self.set_secure_cookie("incorrect", "0")
            self.redirect(self.reverse_url("home"))
        else:
            incorrect = self.get_secure_cookie("incorrect") or 0
            increased = str(int(incorrect)+1)
            self.set_secure_cookie("incorrect", increased)
            self.write("""<center>
                            Something Wrong With Your Data (%s)<br />
                            <a href="/login">Try it again</a>
                          </center>""" % increased)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", self.reverse_url("home")))


class HomeHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("home.jade", title="Partners Capital")


class ResearchHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("research.jade", title="Research - Partners Capital")


class GutenbergHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self, *args, **kwargs):        
        self.render("gutenberg.jade",
                    title="Gutenberg - Partners Capital",
                    message=False)


class ImdbHandler(BaseHandler):

    doc = {
            '_source': ['title', 'film_rating', 'duration',
                        'genre', 'release_date'],
            'query': {
                'match_all' : {}
           },
            'size' : 50,
            'from': 0,
       }

    def initialize(self):
        data = {}
        self.res = self.application.es_conn.search(
            index='imdb', doc_type='doc', body=self.doc, scroll='1m')
        #scrollId = self.res['_scroll_id']    
        #es.scroll(scroll_id = scrollId, scroll = '1m')
    
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        
        all_keys = set()
        content = []
        for row in self.res['hits']['hits']:
            all_keys |= set(row['_source'].keys())
            content.append(row['_source'])
        
   
        self.render("imdb.jade",
                    title ="Imdb - Partners Capital",
                    colnames = all_keys,
                    data = content,
                    message=False)


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

        self.render("tweets.jade",
                    title="tweets",
                    keywords=self.keywords,
                    colnames=colnames,
                    tweets=tweets)

        
class ChartsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("charts.jade", title="charts")


class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("about.jade", title="about")


def gutenberg(message, es_conn):
    doc = {
        "_source": 
        {
            "includes": ["meta.author", "meta.filename", "meta.title",
                         "meta.pages", "created", "meta.path_img"],
            "excludes": ["content_base64"]
        }, 
        "query": {
            "match_all": {}
        },
        "size": 1
    }

    res = es_conn.search(index='files', doc_type='_doc', body=doc, scroll='1m')

    #scrollId = self.res['_scroll_id']    
    #es.scroll(scroll_id = scrollId, scroll = '1m')
    pages = []
    all_keys = set()
    content = []
    hits = res.get('hits')
    res = {}
    
    if hits:
        total = hits.get('total')
        max_score = hits.get('max_score')
        rows = hits.get('hits')
    
        if rows:
            for row in rows:
                _index = row.get('_index')
                _type = row.get('_type')
                _id = row.get('_id')
                _score = row.get('_score')
                _source = row.get('_source')
                
                _meta = _source.get('meta', {})
                author =  _meta.get('author', '')
                title = _meta.get('title', '')
                numpages = _meta.get('pages', '')
                created = _source.get('created', '')
                
                
                all_keys |= set(_source.keys())
                content.append(_source)

                path_img = _source.get('meta', {}).get('path_img')
                folder_name = _source.get('meta', {}).get('filename')
                
                for f in os.listdir(path_img):
                    if os.path.isfile(os.path.join(path_img, f)) and \
                    f.endswith(('.jpg', '.jpeg')):
                        rel_path = os.path.join('static', 'img', 'gutenberg', 
                                                folder_name, f)
                        pages.append(rel_path)
                
                pages.sort()
                
                res = {
                    'author': author,
                    'title': title,
                    'numpages': numpages,
                    'created': created,
                    'pages': pages
                }
    return res


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

    def on_message(self, message):
        recv = json.loads(message)
        path = recv.get('path')
        msg = recv.get('message')
        data = {}
        
        if path and type(path) is str:    
            if path == '/gutenberg':
                if msg and type(msg) is str:
                    data = gutenberg(msg, self.application.es_conn)
        
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
            "time": datetime.datetime.now(),
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        content["html"] = tornado.escape.to_basestring(
            self.render_string("message.jade", message=content))
        
        self.update_cache(content)
        self.send_updates(content)
