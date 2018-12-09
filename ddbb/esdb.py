import logging
from elasticsearch import Elasticsearch
from config import conf_es

es=Elasticsearch(conf_es.get('HOST'),port=conf_es.get('PORT'), verify_certs=True)

if not es.ping():
    raise ValueError("Elasticsearch connection failed")

logging.info('[  OK  ]  Elasticsearch connection')

es.indices.create(index=conf_es.get('INDEX'), ignore=400)

__all__= ['es']
