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

    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index="2021-Q1",
        filter_count=89)
    print('2020-Q4 top 50 股票')
    pprint(stock_top_list)
    print(len(stock_top_list))

    stock_quarter_count = each_statistic.item_stock_fund_count('海螺水泥')
    print("stock_quarter_count", stock_quarter_count)
