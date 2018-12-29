import sys
import os
from elasticsearch import Elasticsearch
from config import config, logger, decfun
import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host=config.get('es',{}).get('host')
port=config.get('es',{}).get('port')

if sock.connect_ex((host, port)) != 0:
   raise ValueError("Error connecting to Elasticsearch on '{}:{}'".
                    format(host, port))

es=Elasticsearch(
    host=config.get('es',{}).get('host'),
    port=config.get('es',{}).get('port'),
    verify_certs=True)

if not es.ping():
    raise ValueError("Elasticsearch is connected but refusing pings")

#logger.info('[  OK  ]  Elasticsearch connection')

es.indices.create(index=config.get('es',{}).get('index'), ignore=400)

__all__= ['es']
