# -*- coding:UTF-8 -*-
'''
Desc: 从基金的持仓中统计股票出现频率
File: /index.py
Project: src
File Created: Monday, 22nd March 2021 12:08:36 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import pymysql
from pprint import pprint
from db.connect import connect

cursor = connect().cursor()

if __name__ == '__main__':
    page_start = 0
    page_limit = 10000
    stock_sql_join = ''
    for index in range(10):
        stock_sql_join = stock_sql_join + \
            "t.top_stock_%s_code, t.top_stock_%s_name" % (
                str(index), str(index)) + ","
    # print(stock_sql_join[0:-1])
    stock_sql_join = stock_sql_join[0:-1]
    # print(stock_sql_join)
    sql_query_season = "SELECT t.fund_code," + stock_sql_join + \
        " FROM fund_morning_stock_info as t WHERE t.quarter_index = '2020-q4' AND t.stock_position_total > 20 LIMIT %s, %s ;"
    cursor.execute(sql_query_season, [page_start, page_limit])    # 执行sql语句
    results = cursor.fetchall()    # 获取查询的所有记录
    # pprint(results)
    code_dict = dict()
    for result in results:
        # print(result)
        for index in range(1, len(result), 2):
            code = result[index]
            name = result[index + 1]
            key = str(code) + '-' + str(name)
            if(key in code_dict and code != None):
                code_dict[key] = code_dict[key] + 1
            else:
                code_dict[key] = 1
    filer_dict = dict()

    for key, value in code_dict.items():  # for (key,value) in girl_dict.items() 这样加上括号也可以
        if value > 100 and key != None:
            filer_dict[key] = value
            # print(key + ":" + str(value))
    list = sorted(filer_dict.items(), key=lambda x: x[1], reverse=True)
    pprint(list)
    # pprint(dir(code_dict))
    # filer_dict = dict((name, getattr(code_dict, name))
    #                   for name in dir(code_dict) if not (name == None or getattr(code_dict, name) > int(1)))
    # pprint(filer_dict)
