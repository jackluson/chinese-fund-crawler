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


def stocks_compare(stock_list, fund_code_pool=None):
    each_statistic = FundStatistic()
    filter_list = []
    for stock in stock_list:
        stock_name = stock[0]
        stock_sum = stock[1]

        stock_quarter_count_tuple = each_statistic.item_stock_fund_count(
            stock_name,
            fund_code_pool
        )
        try:
            last_count_tuple = stock_quarter_count_tuple[len(
                stock_quarter_count_tuple) - 2]
        except:
            print('该股票查询异常', stock_name)
            continue

        last_stock_sum = last_count_tuple[0]  # 选出上一个季度的
        if len(stock_quarter_count_tuple) == 1:
            last_stock_sum = 0

        diff = stock_sum - last_stock_sum

        diff_percent = '{:.2%}'.format(
            diff / last_stock_sum) if last_stock_sum != 0 else "+∞"

        flag = '📈' if diff > 0 else '📉'
        if diff == 0:
            flag = '⏸'
        item_tuple = (stock_name, stock_sum, last_stock_sum,
                      diff, diff_percent, flag)

        if diff_percent == "+∞" or not float(diff_percent.rstrip('%')) < -20:
            filter_list.append(item_tuple)
        print(item_tuple)
    return filter_list


if __name__ == '__main__':
    each_statistic = FundStatistic()

    fund_code_pool = ['000001', '160133', '360014', '420002',
                      '420102', '000409', '000418', '000746',
                      '000751', '000884', '000991', '001043',
                      '001054', '001104', '001410', '001473',
                      '519714', '000003', '000011', '000029']
    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index="2021-Q1",
        fund_code_pool=None,
        filter_count=0)
    # print('2020-Q4 top 100 股票')
    # pprint(stock_top_list)
    print(len(stock_top_list))

    filter_list = stocks_compare(stock_top_list)
    pprint(filter_list)
    pprint(len(filter_list))
