import os
from datetime import datetime
from utils import utils
from ddbb import es
from config import logger

def search_filename(filename):
    logger.info(filename)
    if filename and type(filename) is str:
        query = {
            "_source": {
                "excludes": ["content", "content_base64"]
            },
            "query": {
                "nested": {
                    "path": "meta",
                    "query": {
                        "term": {
                            "meta.filename": {
                                "value": filename
                            }
                        }
                    }
                }
            }
        }
        logger.info(query)
        res = es.search(index='files', doc_type='_doc', body=query, scroll='1m')
        logger.info(res)
        return get_hits(filename, res)


def search_docs(to_search):
    query = {
        "_source": 
        {
            "includes": ["meta.author", "meta.filename", "meta.title",
                         "meta.pages", "meta.folder_file", "meta.folder_img",
                         "meta.filename", "meta.extension", 
                         "created", "summary", "tags"],
            "excludes": ["content_base64"]
        }, 
        "query": {
            "multi_match": {
                "query" : to_search,
                "fields" : ["title^3", "content"]
            }
        },
        "highlight" : {
            "number_of_fragments" : 3,
            "fragment_size" : 150,
            "fields" : {
                "_all" : { "pre_tags" : ["<em>"], "post_tags" : ["</em>"] },
                "meta.title" : { "number_of_fragments" : 0 },
                "meta.author" : { "number_of_fragments" : 0 },
                "summary" : { "number_of_fragments" : 5, "order" : "score" },
                "content" : { "number_of_fragments" : 5, "order" : "score" }
            }
        },
        "size": 50
    }

    res = es.search(index='files', doc_type='_doc', body=query, scroll='1m')

    #scrollId = self.res['_scroll_id']    
    #es.scroll(scroll_id = scrollId, scroll = '1m')
    return get_hits(to_search, res)


def get_hits(to_search, res):
    
    hits = res.get('hits')
    res = {}
    #all_keys = set()
    
    if hits:
        _total = hits.get('total')
        _max_score = hits.get('max_score')
        rows = hits.get('hits')
    
        if rows:
            for row in rows:
                _id = row.get('_id')
                _score = row.get('_score')
                _source = row.get('_source')
                
                _meta = _source.get('meta', {})
                _author =  _meta.get('author', '')
                _title = _meta.get('title', '')
                _numpages = _meta.get('pages', -1)
                _summary = _source.get('summary', '')
                _tags = _source.get('tags', '')
                
                _date = _source.get('created', '1970-01-01 00:00:00')
                d = datetime.strptime(_date, "%Y-%m-%d %H:%M:%S")
                _created = d.strftime("%d-%b-%Y")
                
                _file_folder = _meta.get('folder_file', '')
                _file_img = _meta.get('folder_img', '')
                _file_name = _meta.get('filename', '')
                _file_extension = _meta.get('extension', '')
                _fileurl = os.path.join('public', _file_folder, _file_name + _file_extension)
                #all_keys |= set(_source.keys())
                
                if _summary:
                    _summary = ['<p>' + s + '</p>'for s in _summary.splitlines()]
                    _summary = ' '.join(_summary)
                    if _tags:
                        for t in _tags:
                            _summary = _summary.replace(t, '<strong style="color: #102889">' + t + '</strong>')
                    _summary = _summary.replace(to_search, '<strong style="color: #ff0000">' + to_search + '</strong>')
                
                if _title:
                    _title = _title.replace(to_search, '<strong>' + to_search + '</strong>')
                
                if _tags:
                    _tags = ['<span class="badge badge-secondary" style="font-size:12px;">' + t +'</span>' for t in _tags]
                    _tags = ' '.join(_tags)
                    _tags = '<p>' + _tags + '</p>'
                
                res[_id] = {
                    'author': utils.null_to_emtpy_str(_author),
                    'title': utils.null_to_emtpy_str(_title),
                    'numpages': utils.null_to_emtpy_str(_numpages),
                    'summary': utils.null_to_emtpy_str(_summary),
                    'created': utils.null_to_emtpy_str(_created),
                    'score': utils.null_to_emtpy_str(_score),
                    'max_score': utils.null_to_emtpy_str(_max_score),
                    'total': utils.null_to_emtpy_str(_total),
                    'document': utils.null_to_emtpy_str(_file_img),
                    'fileurl': utils.null_to_emtpy_str(_fileurl),
                    'tags': utils.null_to_emtpy_str(_tags)
                }
    return res
