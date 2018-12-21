import sys
import os
from elasticsearch import Elasticsearch
from config import conf, logger, decfun

es=Elasticsearch(
    host=conf.get('es',{}).get('host'),
    port=conf.get('es',{}).get('port'),
    verify_certs=True)

if not es.ping():
    raise ValueError("Elasticsearch connection failed")

#logger.info('[  OK  ]  Elasticsearch connection')

es.indices.create(index=conf.get('es',{}).get('index'), ignore=400)

__all__= ['es']
