import bcrypt
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapper, relationship, sessionmaker
from config import config


class User():
    
    def __init__(self, name, password, created, last_loggedin):
        self.name = name
        self.password = password
        self.created = created
        self.last_loggedin = last_loggedin
    
    def __repr__(self):
        return ("<User(name='{}', password='{}')>"
                .format(self.name, self.password))


class Contact():
    
    def __init__(self, email):
        self.email = email

    def __repr__(self):
            return ("<Contact(email='{}'>".format(self.email))

class Twitter():
    
    def __init__(self, following):
        self.following = following

    def __repr__(self):
            return ("<Twitter(following='{}'".format(self.following))
                

# Users - database
users_db = config.get('users',{}).get('db')

db_path = users_db.get('path')
db_tbl_users = users_db.get('table_users')
db_tbl_contact = users_db.get('table_contact')
db_tbl_twitter = users_db.get('table_twitter')

# classical mapping: map "table" to "class"
db_url = 'sqlite:///{db}'.format(db=db_path)
engine = create_engine(db_url)

meta = MetaData(bind=engine)

tbl_users = Table(db_tbl_users, meta,
             Column('id', Integer, primary_key=True),
             Column('name', String),
             Column('password', String),
             Column('created', DateTime, default=datetime.utcnow),
             Column('last_loggedin', DateTime))

tbl_contact = Table(db_tbl_contact, meta,
             Column('id', Integer, primary_key=True),
             Column('email', String),
             Column('user_id', Integer, ForeignKey('users.id')))

tbl_twitter = Table(db_tbl_twitter, meta,
             Column('id', Integer, primary_key=True),
             Column('following', String),
             Column('user_id', Integer, ForeignKey('users.id')))

mapper(User, tbl_users, properties={
       'emails': relationship(Contact, backref='users'),
       'following': relationship(Twitter, backref='users')})

mapper(Contact, tbl_contact)
mapper(Twitter, tbl_twitter)

# create table
meta.create_all()

# create session
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

user = (session.query(User,Contact)
        .filter(User.id == Contact.user_id)
        .filter(Contact.email == 'demo@test.com')
        .all())

if not user:
    
    plaintext_password = b'demo'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plaintext_password, salt)
    user = User(name='demo', password=hashed, created=datetime.now(), last_loggedin = None)
    contact = Contact(email='demo@test.com')
    follow = Twitter(following='Trump')

    user.emails.append(contact)
    user.following.append(follow)

    try:
        session.add(user)
        session.commit()
    
    finally:
        session.close()