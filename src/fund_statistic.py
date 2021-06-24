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
        **condition_dict,
    )
    return fund_code_pool

def stocks_compare(stock_list, fund_code_pool=None):
    each_statistic = FundStatistic()
    last_quarter_index = get_last_quarter_str(2)

    filter_list = []
    for stock in stock_list:
        stock_code = stock[0].split('-', 1)[0]
        if not stock_code:
            continue
        stock_name = stock[0].split('-', 1)[1]
        stock_sum = stock[1]

        stock_quarter_count_tuple = each_statistic.item_stock_fund_count(
            stock_code,
            fund_code_pool
        )
        last_stock_sum = 0
        print("stock_quarter_count_tuple", stock_quarter_count_tuple)
        for item in stock_quarter_count_tuple:
            quarter_index_str = item[1]
            if quarter_index_str == last_quarter_index:
                last_stock_sum = item[0]
                break

        diff = stock_sum - last_stock_sum

        diff_percent = '{:.2%}'.format(
            diff / last_stock_sum) if last_stock_sum != 0 else "+∞"

        # flag = '📈' if diff > 0 else '📉'
        # if diff == 0:
        #     flag = '⏸'
        flag = 'up' if diff > 0 else 'down'
        if diff == 0:
            flag = '='
        item_tuple = (stock_code, stock_name, stock_sum, last_stock_sum,
                      diff, diff_percent, flag)

        # if diff_percent == "+∞" or not float(diff_percent.rstrip('%')) < -20:
        filter_list.append(item_tuple)
        # print(item_tuple)
    return filter_list

# 股票排名
def rank_stock(each_statistic, threshold=80):
    quarter_index = get_last_quarter_str()
    last_quarter_index = get_last_quarter_str(2)
    output_file = './outcome/数据整理/strategy/top100_rank.xlsx'
    sheet_name = quarter_index + '基金重仓股T100'
    columns=['代码',
        '名称', quarter_index + '持有数量（只）', last_quarter_index + '持有数量（只）', '环比', '环比百分比', '升Or降']
    if threshold == 0:
        output_file = './outcome/数据整理/strategy/'+ quarter_index +'-all_stock_rank.xlsx'

    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index=quarter_index,
        filter_count=threshold)
    if threshold != 0:
        stock_top_list = stock_top_list[:100]
    #pprint(stock_top_list)
    if threshold != 0:
        filter_list = stocks_compare(stock_top_list)
        df_filter_list = pd.DataFrame(filter_list, columns=columns)
        df_filter_list.to_excel(output_file, sheet_name=sheet_name)
    else:
        other_stock_list = []
        hk_stock_list = []
        a_stock_list = []
        for stock_name_code in stock_top_list:
            #print(stock_name_code[0])
            stock_code = stock_name_code[0].split('-', 1)[0]
            #path = 'other'
            if bool(re.search("^\d{5}$", stock_code)):
                #path = '港股'
                hk_stock_list.append(stock_name_code)
            elif bool(re.search("^\d{6}$", stock_code)):
                if bool(re.search("^00(0|1|2|3)\d{3}$", stock_code)):
                    #path = 'A股/深证主板'
                    a_stock_list.append(stock_name_code)
                elif bool(re.search("^300\d{3}$", stock_code)):
                    #path = 'A股/创业板'
                    a_stock_list.append(stock_name_code)
                elif bool(re.search("^60(0|1|2|3|5)\d{3}$", stock_code)):
                    #path = 'A股/上证主板'
                    a_stock_list.append(stock_name_code)
                elif bool(re.search("^68(8|9)\d{3}$", stock_code)):
                    #path = 'A股/科创板'
                    a_stock_list.append(stock_name_code)
                else:
                    other_stock_list.append(stock_name_code)
            else:
                other_stock_list.append(stock_name_code)

        a_stock_compare_list = stocks_compare(a_stock_list)
        hk_stock_compare_list = stocks_compare(hk_stock_list)
        other_stock_compare_list = stocks_compare(other_stock_list)

        df_a_list = pd.DataFrame(a_stock_compare_list, columns=columns)
        df_hk_list = pd.DataFrame(hk_stock_compare_list, columns=columns)
        df_other_list = pd.DataFrame(other_stock_compare_list, columns=columns)

        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        df_a_list.to_excel(writer, sheet_name='A股')

        df_hk_list.to_excel(writer, sheet_name='港股')

        df_other_list.to_excel(writer, sheet_name='其他')

        writer.save()


def all_stock(quarter_index, each_statistic, threshold=0):
    stock_list = each_statistic.all_stock_fund_count_and_details(
        quarter_index=quarter_index,
        filter_count=threshold)
    for i in range(0, 500):
        stock = stock_list[i]
        stock_name_code = stock[0]
        stock_code = stock_name_code.split('-', 1)[0]
        path = '其他'
        if bool(re.search("^\d{5}$", stock_code)):
            path = '港股'
        elif bool(re.search("^\d{6}$", stock_code)):
            if bool(re.search("^00(0|1|2|3)\d{3}$", stock_code)):
                path = 'A股/深证主板'
            elif bool(re.search("^300\d{3}$", stock_code)):
                path = 'A股/创业板'
            elif bool(re.search("^60(0|1|2|3|5)\d{3}$", stock_code)):
                path = 'A股/上证主板'
            elif bool(re.search("^68(8|9)\d{3}$", stock_code)):
                path = 'A股/科创板'
            else:
                print('stock_name_code', stock_name_code)
            #path = 'A股'
        hold_fund_count = stock[1]['count']
        hold_fund_list = stock[1]['fund_list']
        df_list = pd.DataFrame(hold_fund_list)
        stock_name_code = stock_name_code.replace('-*', '-').replace('/', '-')
        path = './outcome/数据整理/stocks/' + path + '/' + stock_name_code + '.xlsx'
        path = path.replace('\/', '-')
        print("path", path)
        #print('df_list--',stock_name_code, df_list)
        if os.path.exists(path):
            writer = pd.ExcelWriter(path, engine='openpyxl')
            book = load_workbook(path)
            # 表名重复，删掉，重写
            if quarter_index in book.sheetnames:
                del book[quarter_index]
            if len(book.sheetnames) == 0:
                df_list.to_excel(
                path, sheet_name=quarter_index)
                continue
            else:
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
    quarter_index = "2021-Q1"
    # 获取重仓股
    #rank_stock(each_statistic, 0)

    # 所有股票的基金持仓细节
    all_stock(quarter_index, each_statistic)
