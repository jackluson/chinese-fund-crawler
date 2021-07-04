'''
Desc: 股票查询
File: /stock_query.py
Project: sql_model
File Created: Wednesday, 30th June 2021 3:29:07 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from db.connect import connect_dict

class StockQuery:
    def __init__(self):
        connect_instance = connect_dict()
        self.connect = connect_instance.get('connect')
        self.cursor = connect_instance.get('cursor')
        self.dict_cursor = connect_instance.get('dict_cursor')

    def query_all_stock(self):
        query_stock_sql = "SELECT stock_code, industry_name_first, industry_name_second, industry_name_third FROM stock_industry"
        self.dict_cursor.execute(query_stock_sql)
        results = self.dict_cursor.fetchall()
        return results
    # 查询股票对应行业
    def query_stock_industry(self, stock_code_pool):
        if isinstance(stock_code_pool, list):
            if len(stock_code_pool) == 0:
                return ()
            temp = "%s," * len(stock_code_pool)
            stock_sql_join = temp[0:-1]
        sql = "SELECT stock_code, stock_name, industry_name_first, industry_name_second, industry_name_third FROM stock_industry WHERE stock_code IN ( " + stock_sql_join + " )"
        self.dict_cursor.execute(sql, stock_code_pool)
        results = self.dict_cursor.fetchall()
        return results
