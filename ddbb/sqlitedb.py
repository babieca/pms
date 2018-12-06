import os
import sqlite3

class SQLite():
    
    def __init__(self, sqlite_path , sqlite_ddbbname, sqlite_tablename, delete=False):
        self.__path = sqlite_path
        self.__ddbbname = sqlite_ddbbname
        self.__tablename = sqlite_tablename
        self.__conn = None
        if delete and os.path.isfile(sqlite_path):
            os.remove(sqlite_path)
        self.connect()

    def connect(self):
        self.__conn = sqlite3.connect(self.__path)   
        
    def create(self, sqlite_query):
        dbcursor = self.__conn.cursor()
        dbcursor.execute(sqlite_query)
        self.__conn.commit()
    
    
    def insert(self, data):
        
        # data = {'column1': 'value1', 'column2': 'value2', 'column3': 'value3'}
        
        # ['column1', 'column3', 'column2']
        columns = data.keys()  
        
        # 'column1, column3, column2'
        placeholder_columns = ", ".join(data.keys())
        
        # ':column1, :column3, :column2'
        placeholder_values = ", ".join([":{0}".format(col) for col in columns])
        
        
        sql = "INSERT INTO {table_name} ({placeholder_columns}) VALUES ({placeholder_values})".format(
            table_name='twitter',
            placeholder_columns=placeholder_columns,
            placeholder_values=placeholder_values
        )
        
        # 'INSERT INTO table_name (column1, column3, column2) VALUES (:column1, :column3, :column2)'
        dbcursor = self.__conn.cursor()
        dbcursor.execute(sql, data)
        self.__conn.commit()
    
    def select(self, strSQL):
        dbcursor = self.__conn.cursor()
        dbcursor.execute(strSQL)
        allrows = dbcursor.fetchall()
        
        data = [dict((dbcursor.description[i][0], value) \
                     for i, value in enumerate(row)) for row in allrows]

        return data
        
    def close(self):
        self.__conn.close()
    
__all__ = ['SQLite']
