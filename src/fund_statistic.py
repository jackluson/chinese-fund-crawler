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
from sql_model.fund_query import FundQuery

cursor = connect().cursor()

if __name__ == '__main__':
    each_query = FundQuery()
    query_index = '2021-Q1'
    results = each_query.select_top_10_stock(query_index)
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
    print(len(list))
    pprint(list)
    # pprint(dir(code_dict))
    # filer_dict = dict((name, getattr(code_dict, name))
    #                   for name in dir(code_dict) if not (name == None or getattr(code_dict, name) > int(1)))
    # pprint(filer_dict)
