#!/usr/bin/env python
import sys
sys.path.insert(0, '../config/')
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, relationship, sessionmaker
from config import config

class User():
    
    def __init__(self, name, password):
        self.name = name
        self.password = password


class Contact():
    
    def __init__(self, email):
        self.email = email


class Twitter():
    
    def __init__(self, following):
        self.following = following


def run():
    
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
                 Column('password', String))
    
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
    
    user = User(name='demo', password='demo')
    contact = Contact(email='demo@test.com')
    follow = Twitter(following='Trump')
    
    user.emails.append(contact)
    user.following.append(follow)
    
    try:
        session.add(user)
        session.commit()
    
        # query result
        user = session.query(User).filter(User.name == 'demo').first()
        print(("User: '{}' with id '{}' and password: '{}' " + 
                      "was created successfully").format(
                          user.id, user.name, user.password))
    
    finally:
        session.close()

if __name__ == '__main__':
    run()