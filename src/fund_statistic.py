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
        filter_count=90)
    print('2020-Q4 top 100 股票')
    # pprint(stock_top_list)
    print(len(stock_top_list))
    filter_list = []

    for stock in stock_top_list:
        stock_name = stock[0]
        stock_sum = stock[1]

        stock_quarter_count_tuple = each_statistic.item_stock_fund_count(
            stock_name)
        last_count_tuple = stock_quarter_count_tuple[len(
            stock_quarter_count_tuple) - 2]  # 选出上一个季度的
        diff = stock_sum - last_count_tuple[0]

        diff_percent = '{:.2%}'.format(
            diff / last_count_tuple[0])
        flag = '📈' if diff > 0 else '📉'
        if diff == 0:
            flag = '⏸'
        item_tuple = (stock_name, stock_sum, last_count_tuple[0],
                      diff, diff_percent, flag)
        if not float(diff_percent.rstrip('%')) < -20:
            filter_list.append(item_tuple)
        print(item_tuple)
    pprint(filter_list)
    pprint(len(filter_list))
