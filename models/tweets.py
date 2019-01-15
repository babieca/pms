from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, DateTime
from sqlalchemy.orm import mapper
from config import config, logger


class Tweets():
    
    def __init__(self, created_at, id_str, tweet, user_name, user_screen_name,
                 user_followers_count, user_created_at, user_location, keyword):
        self.created_at = created_at
        self.id_str = id_str
        self.tweet = tweet
        self.user_name = user_name
        self.user_screen_name = user_screen_name
        self.user_followers_count = user_followers_count
        self.user_created_at = user_created_at
        self.user_location = user_location
        self.keyword = keyword
    
    def __repr__(self):
        return ("<Tweets(id_str='{}', created_at='{}', user_name='{}', "
                "user_followers_count='{}', tweet='{}')>"
                .format(self.id_str, self.created_at, self.user_name,
                        self.user_followers_count, self.tweet))

# Twitter - database
twitter_db = config.get('twitter',{}).get('db')
db_path = twitter_db.get('path')
db_tbl = twitter_db.get('table')


# classical mapping: map "table" to "class"
db_url = 'sqlite:///{db}'.format(db=db_path)

engine = create_engine(db_url)
engine.echo = False

meta = MetaData(bind=engine)

tbl_twitter = Table(db_tbl, meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('keyword', String, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('id_str', String, nullable=False),
    Column('tweet', String, nullable=False),
    Column('source', String),
    Column('truncated', Integer),
    Column('user_id_str', String),
    Column('user_name', String, nullable=False),
    Column('user_screen_name', String),
    Column('user_location', String),
    Column('user_description', String),
    Column('user_followers_count', Integer),
    Column('user_friends_count', Integer),
    Column('user_created_at', DateTime),
    Column('user_utc_offset', String),
    Column('user_time_zone', String),
    Column('user_lang', String),
    Column('retweeted_created_at', String),
    Column('retweeted_id_str', String),
    Column('retweeted_text', String),
    Column('retweeted_source', String),
    Column('retweeted_truncated', Integer),
    Column('retweeted_user_id_str', String),
    Column('retweeted_user_name', String),
    Column('retweeted_user_screen_name', String),
    Column('retweeted_user_location', String),
    Column('retweeted_user_description', String),
    Column('retweeted_user_followers_count', Integer),
    Column('retweeted_user_friends_count', Integer),
    Column('retweeted_user_created_at', DateTime),
    Column('retweeted_user_lang', String),
    autoload=True, autoload_with=engine)

mapper(Tweets, tbl_twitter)

meta.drop_all()
# create table
meta.create_all()
