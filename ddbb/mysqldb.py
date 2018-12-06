
from config import conf_mysql
from ddbb import MySQLPython

dbconn = MySQLPython(conf_mysql.get('MYSQL_HOST'), conf_mysql.get('MYSQL_PORT'),
                      conf_mysql.get('MYSQL_USERNAME'), conf_mysql.get('MYSQL_PASSWORD'),
                      conf_mysql.get('MYSQL_DB'))


def items2listen(query):
             
    res = dbconn.mysql_select(sql)
    to_search = ''
    kw = []
    for i, company in enumerate(d['short_name'] for d in res):
        kw.append(company.lower().partition(' ')[0])
    return kw


query = "SELECT t1.ticker, t1.short_name, t2.amount " \
            "FROM assets AS t1, " \
            "(SELECT trd_ticker AS ticker, SUM(trd_filled) AS amount " \
            "FROM fundtrades GROUP BY trd_ticker) AS t2 " \
            "WHERE t1.ticker = t2.ticker " \
            "AND t2.amount != 0"


__all__ = ['dbconn']