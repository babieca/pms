from elasticsearch import Elasticsearch
from config import conf_es


#es=Elasticsearch(['localhost'],http_auth=('elastic', 'changeme'),port=9200)
es=Elasticsearch(conf_vars.get('ES_HOST'),port=conf_vars.get('ES_PORT'))

es.indices.create(index=conf_es.get('INDEX'), ignore=400)

def print_search_stats(results):
    print('=' * 80)
    print('Total {} found in {}'.format(results['hits']['total'], results['took']))
    print('-' * 80)

def print_hits(results):
    " Simple utility function to print results of a search query. "
    print_search_stats(results)
    for hit in results['hits']['hits']:
        # get created date for a repo and fallback to authored_date for a commit
        created_at = parse_date(hit['_source'].get('created_at', hit['_source']['authored_date']))
        print('/{}/{}/{} ({}): {}'.format(
                hit['_index'], hit['_type'], hit['_id'],
                created_at.strftime('%Y-%m-%d'),
                hit['_source']['description'].split('\n')[0]))

    print('=' * 80)
    print()


__all__= ['es', 'print_search_stats', 'print_hits']