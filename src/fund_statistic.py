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
import time
import re
from pprint import pprint
import pandas as pd
from fund_info.statistic import FundStatistic
from utils.index import get_last_quarter_str
from openpyxl import load_workbook
import os

def get_fund_code_pool():
    # fund_code_pool = ['000001', '160133', '360014', '420002',
    #                   '420102', '000409', '000418', '000746',
    #                   '000751', '000884', '000991', '001043',
    #                   '001054', '001104', '001410', '001473',
    #                   '519714', '000003', '000011', '000029']
    morning_star_rating_5_condition = {
        'value': 4,
        'operator': '>='
    }
    morning_star_rating_3_condition = {
        'value': 5,
        'operator': '='
    }
    last_year_time = time.localtime(time.time() - 365 * 24 * 3600)
    last_year_date = time.strftime('%Y-%m-%d', last_year_time)
    condition_dict = {
        'morning_star_rating_5': morning_star_rating_5_condition,
        'morning_star_rating_3': morning_star_rating_3_condition,
        # 'manager_start_date': '2020-05-25'
    }
    fund_code_pool = each_statistic.select_fund_pool(
    #    **condition_dict,
    #)
    return fund_code_pool

def stocks_compare(stock_list, fund_code_pool=None):
    each_statistic = FundStatistic()
    filter_list = []
    for stock in stock_list:
        stock_code = stock[0].split('-', 1)[0]
        stock_name = stock[0].split('-', 1)[1]
        stock_sum = stock[1]

        stock_quarter_count_tuple = each_statistic.item_stock_fund_count(
            stock_code,
            fund_code_pool
        )
        try:
            last_count_tuple = stock_quarter_count_tuple[len(
                stock_quarter_count_tuple) - 2]
        except:
            print("stock_quarter_count_tuple", stock_quarter_count_tuple)
            print('该股票查询异常', stock_code, stock_name)
            continue

        last_stock_sum = last_count_tuple[0]  # 选出上一个季度的
        if len(stock_quarter_count_tuple) == 1:
            last_stock_sum = 0

        diff = stock_sum - last_stock_sum

        diff_percent = '{:.2%}'.format(
            diff / last_stock_sum) if last_stock_sum != 0 else "+∞"

        # flag = '📈' if diff > 0 else '📉'
        # if diff == 0:
        #     flag = '⏸'
        flag = 'up' if diff > 0 else 'down'
        if diff == 0:
            flag = '='
        item_tuple = (stock_name, stock_sum, last_stock_sum,
                      diff, diff_percent, flag)

        # if diff_percent == "+∞" or not float(diff_percent.rstrip('%')) < -20:
        filter_list.append(item_tuple)
        # print(item_tuple)
    return filter_list

def top100_stock(each_statistic, threshold=80):
    quarter_index = get_last_quarter_str()
    last_quarter_index = get_last_quarter_str(2)
    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index=quarter_index,
        filter_count=threshold)[:100]
    # print('2020-Q4 top 100 股票')
    pprint(stock_top_list)
    #print(len(stock_top_list))

    filter_list = stocks_compare(stock_top_list)

    #pprint(filter_list)
    pprint(len(filter_list))
    df_filter_list = pd.DataFrame(filter_list, columns=[
        '名称', quarter_index + '持有数量（只）', last_quarter_index + '持有数量（只）', '环比', '环比百分比', '升Or降'])
    df_filter_list.to_excel(
        './outcome/strategy/top100.xlsx', sheet_name=quarter_index + '基金重仓股T100')

def all_stock(each_statistic, threshold=0):
    quarter_index = "2021-Q1"
    stock_list = each_statistic.all_stock_fund_count_and_details(
        quarter_index=quarter_index,
        filter_count=threshold)
    for i in range(0, len(stock_list)):
        stock = stock_list[i]
        stock_name_code = stock[0]
        stock_code = stock_name_code.split('-', 1)[0]
        path = 'other'
        if bool(re.search("^\d{5}$", stock_code)):
            path = 'hk'
        elif bool(re.search("^\d{6}$", stock_code)):
            path = 'a'
        hold_fund_count = stock[1]['count']
        hold_fund_list = stock[1]['fund_list']
        df_list = pd.DataFrame(hold_fund_list)
        stock_name_code = stock_name_code.replace('/', '-')
        path = './outcome/stocks/' + path + '/' + stock_name_code + '.xlsx'
        path = path.replace('\/', '-')
        if os.path.exists(path):
            writer = pd.ExcelWriter(path, engine='openpyxl')
            book = load_workbook(path)
            writer.book = book
            df_list.to_excel(
                writer, sheet_name=quarter_index)
            writer.save()
            writer.close()
        else:
            df_list.to_excel(
                path, sheet_name=quarter_index)

if __name__ == '__main__':
    each_statistic = FundStatistic()
    # 获取重仓股
    top100_stock(each_statistic)

    # 所有股票的基金持仓细节
    #all_stock(each_statistic)
