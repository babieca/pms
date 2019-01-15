import os
from datetime import datetime
from utils import utils
from ddbb import es
from config import logger

def search_by_filename(filename):
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
        res = es.search(index='files', doc_type='_doc', body=query, scroll='1m')
        return get_hits(filename, res)
    

def search_by_filename_and_folder(filename, folder_file):
    if (filename and type(filename) is str and
        folder_file and type(folder_file) is str):
        query = {
            "_source": {
                "includes": ["meta.title", "meta.pages", "tags", "created", "summary"]
            },
            "query": {
                "nested": {
                    "path": "meta",
                    "query": {
                        "bool": {
                            "must": [ {
                                "term": {
                                    "meta.filename": {
                                        "value": filename
                                    }
                                }
                            },
                            {
                                "term": {
                                    "meta.folder_file": {
                                        "value": folder_file
                                    }
                                }
                            }
                            ]
                        }
                    }
                }
            }
        }
        res = es.search(index='files', doc_type='_doc', body=query, scroll='1m')
        hits = res.get('hits')
        res = {}
        #all_keys = set()
        
        if hits:
            rows = hits.get('hits')
            if rows:
                for row in rows:
                    _id = row.get('_id')
                    _source = row.get('_source')
                    _meta = _source.get('meta', {})
                    _title = _meta.get('title', '')
                    _numpages = _meta.get('pages', -1)
                    _tags = _source.get('tags', '')
                    _summary = _source.get('summary', '')
                    
                    _date = _source.get('created', '1970-01-01 00:00:00')
                    d = datetime.strptime(_date, "%Y-%m-%d %H:%M:%S")
                    _created = d.strftime("%d-%b-%Y")
                    
                    if _summary:
                        _summary = _summary.splitlines()
                        _summary = _summary[0]
                    res[_id] = {
                        'title': utils.null_to_emtpy_str(_title),
                        'numpages': utils.null_to_emtpy_str(_numpages),
                        'summary': utils.null_to_emtpy_str(_summary),
                        'created': utils.null_to_emtpy_str(_created),
                        'tags': utils.null_to_emtpy_str(_tags)
                    }

        return res


def search_docs(should=None, must=None, must_not=None,
                sector=None, date_from=None, date_to=None):
    query = {
        "_source": 
        {
            "includes": ["meta.author", "meta.filename", "meta.title",
                         "meta.pages", "meta.folder_file", "meta.folder_img",
                         "meta.filename", "meta.extension", 
                         "created", "summary", "tags", "sentiment"],
            "excludes": ["content_base64"]
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
        "size": 100
    }

    if not should and not must and must_not:
        # 001
        query["query"] = {
            "bool": {
                "must_not": [
                    {"multi_match": {
                        "query": must_not,
                        "fields": ["title^3", "content"]
                    }}
                ]
            }
        }
    elif not should and must and not must_not:
        # 010
        query["query"] = {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": must,
                        "fields": ["title^3", "content"]
                    }}
                ]
            }
        }
    elif not should and must and must_not:
        # 011
        query["query"] = {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": must,
                        "fields": ["title^3", "content"]
                    }}
                ],
                "must_not": [
                    {"multi_match": {
                        "query": must_not,
                        "fields": ["title^3", "content"]
                    }}
                ]
            }
        }
    elif should and not must and not must_not:
        # 100
        query["query"] = {
            "bool": {
                "should": [
                    {"multi_match": {
                        "query" : should,
                        "fields" : ["title^3", "content"]
                    }}
                ]
            }
        }  
    elif should and not must and must_not:
        # 101
        query["query"] = {
            "bool": {
                "should": [
                    {"multi_match": {
                        "query" : should,
                        "fields" : ["title^3", "content"]
                    }}
                ],
                "must_not": [
                    {"multi_match": {
                        "query": must_not,
                        "fields": ["title^3", "content"]
                    }}
                ]
            }
        }
    elif should and must and not must_not:
        # 110
        query["query"] = {
            "bool": {
                "should": [
                    {"multi_match": {
                        "query" : should,
                        "fields" : ["title^3", "content"]
                    }}
                ],
                "must": [
                    {"multi_match": {
                        "query": must,
                        "fields": ["title^3", "content"]
                    }}
                ]
            }
        }
    elif should and must and must_not:
        # 111
        query["query"] = {
            "bool": {
                "should": [
                    {"multi_match": {
                        "query" : should,
                        "fields" : ["title^3", "content"]
                    }}
                ],
                "must": [
                    {"multi_match": {
                        "query": must,
                        "fields": ["title^3", "content"]
                    }}
                ],
                "must_not": [
                    {"multi_match": {
                        "query": must_not,
                        "fields": ["title^3", "content"]
                    }}
                ]
            }
        }
    
    sector_index = {
        1: 'commodities',
        2: 'credit',
        3: 'cross_assets',
        4: 'economics',
        5: 'emerging_markets',
        6: 'equity',
        7: 'fx_strategy',
        8: 'interest_rate_strategy',
        9: 'others'}
    
    if sector or date_from or date_to:
        if sector:
            sector = int(sector)
            if sector>0:
                if not "query" in query:
                    query["query"] = {}
                if not "bool" in query["query"]:
                    query["query"]["bool"] = {}
                query["query"]["bool"]["filter"] = []
                
                if sector and sector>0:
                    filter_sector = {
                            "nested": {
                                "path": "meta",
                                "query": {
                                    "term": {
                                        "meta.folder_file": {
                                            "value": "files/" + sector_index.get(sector)
                                        }
                                    }
                                }
                            }
                        }
                    query["query"]["bool"]["filter"].append(filter_sector)
        if date_from and not date_to:
            filter_date = {
                "range": {
                    "created": {
                        "gte": date_from,
                        "format": "dd/MM/yyyy"
                    }
                }
            }
            query["query"]["bool"]["filter"].append(filter_date)
        elif not date_from and date_to:
            filter_date = {
                "range": {
                    "created": {
                        "lte": date_to,
                        "format": "dd/MM/yyyy"
                    }
                }
            }
            query["query"]["bool"]["filter"].append(filter_date)
        elif date_from and date_to:
            filter_date = {
                "range": {
                    "created": {
                        "gte": date_from,
                        "lte": date_to,
                        "format": "dd/MM/yyyy||dd/MM/yyyyy"
                    }
                }
            }
            query["query"]["bool"]["filter"].append(filter_date)
    logger.info(query)
    res = es.search(index='files', doc_type='_doc', body=query, scroll='1m')

    #scrollId = self.res['_scroll_id']    
    #es.scroll(scroll_id = scrollId, scroll = '1m')
    return get_formatted_hits(should, res)

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


def get_formatted_hits(to_search, data):
    hits = data.get('hits')
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
                _sentiment = _source.get('sentiment', '')
                
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
                    
                    if to_search:
                        _summary = _summary.replace(to_search, '<strong style="color: #ff0000">' + to_search + '</strong>')
                
                if _title:
                    _title = _title.replace(to_search, '<strong>' + to_search + '</strong>')
                
                if _tags:
                    formatted_tags = ['<span class="badge badge-secondary" style="font-size:12px;">' + t +'</span>' for t in _tags]
                    formatted_tags = ' '.join(formatted_tags)
                    formatted_tags = '<p>' + formatted_tags + '</p>'
                
                _new_summary = []
                if _sentiment:
                    for row in _sentiment:
                        s = ''
                        if row['label'] == 'pos':
                            s = '<p style="color: #267c2c">' + row['sentence'] + '</p>'
                        elif row['label'] == 'neg':
                            s = '<p style="color: #f44242">' + row['sentence'] + '</p>'
                        else:    
                            s = '<p>' + row['sentence'] + '</p>'
                        if _tags:
                            for t in _tags:
                                s = s.replace(t, '<strong>' + t + '</strong>')
                        if to_search:
                            s = s.replace(to_search, '<strong style="color: #26287c">' + to_search + '</strong>')
                        _new_summary.append(s)
                if _new_summary: _summary = ' '.join(_new_summary)
                
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
                    'tags': utils.null_to_emtpy_str(formatted_tags)
                }
    return res
