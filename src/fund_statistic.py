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
from fund_info.statistic import FundStatistic

# cursor = connect().cursor()

if __name__ == '__main__':
    each_statistic = FundStatistic()
    stock_top_list = each_statistic.statistic_stock_fund_count(
        filter_count=88)
    pprint(stock_top_list)
    print(len(stock_top_list))
