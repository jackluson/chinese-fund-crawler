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
import re
import decimal
from functools import cmp_to_key
from pprint import pprint
import pandas as pd
import numpy as np
from fund_info.statistic import FundStatistic
from utils.index import get_last_quarter_str, get_stock_market, find_from_list_of_dict, update_xlsx_file, update_xlsx_file_with_sorted, update_xlsx_file_with_insert
from utils.file_op import read_dir_all_file


def get_fund_code_pool(condition_dict):
    each_statistic = FundStatistic()
    morning_star_rating_5_condition = {
        'value': 4,
        'operator': '>='
    }
    morning_star_rating_3_condition = {
        'value': 5,
        'operator': '='
    }
    # last_year_time = time.localtime(time.time() - 365 * 24 * 3600)
    # last_year_date = time.strftime('%Y-%m-%d', last_year_time)
    fund_code_pool = each_statistic.select_fund_pool(
        **condition_dict,
    )
    return fund_code_pool


def stocks_compare(stock_list, *, market=None, quarter_index=None, is_A_stock=None):
    """与某个季度数据进行比较
    """
    if quarter_index == None:
        quarter_index = get_last_quarter_str(2)
    print("比较-->quarter_index", quarter_index)

    last_quarter_input_file = './outcome/数据整理/strategy/all_stock_rank/' + \
        quarter_index + '.xlsx'
    data_last_quarter = pd.read_excel(
        io=last_quarter_input_file, engine="openpyxl",  dtype={"代码": np.str}, sheet_name=None)

    if market:
        df_data_target_market = data_last_quarter.get(market)
        df_data_target_market[quarter_index +
                              '持有数量（只）'] = df_data_target_market[quarter_index + '持有数量（只）'].astype(int)

    filter_list = []
    for stock in stock_list:
        stock_code = stock[0].split('-', 1)[0]
        if not stock_code:
            continue
        stock_name = stock[0].split('-', 1)[1]
        stock_holder_detail = stock[1]
        holder_count = stock_holder_detail.get('count')
        holder_asset = stock_holder_detail.get('holder_asset')
        if not market:
            target_market = get_stock_market(stock_code)
            df_data_target_market = data_last_quarter.get(target_market)
        target_loc = df_data_target_market[df_data_target_market['代码'] == stock_code]
        last_holder_count = 0
        last_holder_asset = 0
        if len(target_loc) == 1:
            col_target = quarter_index + '持有数量（只）'
            last_holder_count = target_loc[col_target].iloc[0]
            col_target = quarter_index + '持有市值（亿元）'
            last_holder_asset = round(decimal.Decimal(
                target_loc[col_target].iloc[0]), 4)
        diff_holder_count = holder_count - last_holder_count
        diff_holder_asset = holder_asset - last_holder_asset
        diff_holder_count_percent = '{:.2%}'.format(
            diff_holder_count / last_holder_count) if last_holder_count != 0 else "+∞"
        diff_holder_asset_percent = '{:.2%}'.format(
            diff_holder_asset / last_holder_asset) if last_holder_asset != 0 else "+∞"
        # flag = '📈' if diff_holder_count > 0 else '📉'
        # if diff_holder_count == 0:
        #     flag = '⏸'
        flag_count = 'up' if diff_holder_count > 0 else 'down'
        flag_asset = 'up' if diff_holder_asset > 0 else 'down'

        item_tuple = [stock_code, stock_name, holder_count, last_holder_count,
                      diff_holder_count, diff_holder_count_percent, flag_count, holder_asset, last_holder_asset, diff_holder_asset, diff_holder_asset_percent, flag_asset]
        if is_A_stock:
            industry_name_third = stock_holder_detail.get(
                'industry_name_third')
            industry_name_second = stock_holder_detail.get(
                'industry_name_second')
            industry_name_first = stock_holder_detail.get(
                'industry_name_first')
            item_tuple = [*item_tuple, industry_name_third,
                          industry_name_second, industry_name_first]

        # if diff_percent == "+∞" or not float(diff_percent.rstrip('%')) < -20:
        filter_list.append(item_tuple)
        # print(item_tuple)
    return filter_list


def select_condition_stocks_rank(each_statistic=None, *, quarter_index=None):
    if each_statistic == None:
        each_statistic = FundStatistic()
    if quarter_index == None:
        quarter_index = get_last_quarter_str(1)
    columns = ['代码', '名称', '持有数量（只）', '持有市值（亿元）']
    company = '广发基金管理有限公司'
    company_condition = {
        'value': company,
        'operator': '='
    }
    output_file = './outcome/数据整理/stocks/condition/' + company + '.xlsx'
    condition_dict = {
        # 'morning_star_rating_5': morning_star_rating_5_condition,
        # 'morning_star_rating_3': morning_star_rating_3_condition,
        'company': company_condition
    }
    fund_pool = get_fund_code_pool(condition_dict)
    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index=quarter_index,
        fund_code_pool=fund_pool,
        filter_count=0)
    stock_rank_list = []
    for stock_name_code in stock_top_list:
        stock_code = stock_name_code[0].split('-', 1)[0]
        stock_name = stock_name_code[0].split('-', 1)[1]
        stock_count = stock_name_code[1]['count']
        stock_holder_asset = stock_name_code[1]['holder_asset']
        stock_rank_item = [stock_code, stock_name,
                           stock_count, stock_holder_asset]
        stock_rank_list.append(stock_rank_item)
    df_stock_top_list = pd.DataFrame(stock_rank_list, columns=columns)
    print(df_stock_top_list)

    update_xlsx_file(output_file, df_stock_top_list, quarter_index)


def t100_stocks_rank(each_statistic=None, *, quarter_index=None):
    # T100权重股排名
    if each_statistic == None:
        each_statistic = FundStatistic()
    if quarter_index == None:
        quarter_index = get_last_quarter_str(1)
    last_quarter_index = get_last_quarter_str(2)
    output_file = './outcome/数据整理/strategy/基金重仓股Top100.xlsx'
    sheet_name = quarter_index
    columns = ['代码', '名称', quarter_index + '持有数量（只）', last_quarter_index + '持有数量（只）', '持有数量环比', '持有数量环比百分比',
               '持有数量升或降',  quarter_index + '持有市值（亿元）', last_quarter_index + '持有市值（亿元）', '持有市值环比', '持有市值环比百分比', '持有市值升或降']

    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index=quarter_index,
        filter_count=80)
    stock_top_list = stock_top_list[:100]  # 获取top100权重股
    filter_list = stocks_compare(stock_top_list)
    df_filter_list = pd.DataFrame(filter_list, columns=columns)
    update_xlsx_file_with_insert(output_file, df_filter_list, sheet_name)
    # df_filter_list.to_excel(output_file, sheet_name=sheet_name)


def all_stocks_rank(each_statistic=None):
    if each_statistic == None:
        each_statistic = FundStatistic()
    """所有股票排名
    """
    quarter_index = get_last_quarter_str(1)
    print("该quarter_index为", quarter_index)
    last_quarter_index = get_last_quarter_str(2)
    columns = ['代码', '名称', quarter_index + '持有数量（只）', last_quarter_index + '持有数量（只）', '持有数量环比', '持有数量环比百分比',
               '持有数量升或降',  quarter_index + '持有市值（亿元）', last_quarter_index + '持有市值（亿元）', '持有市值环比', '持有市值环比百分比', '持有市值升或降']
    output_file = './outcome/数据整理/strategy/all_stock_rank/' + quarter_index + '.xlsx'

    stock_top_list = each_statistic.all_stock_fund_count(
        quarter_index=quarter_index,
        filter_count=0)
    all_a_stocks_industry_info_list = each_statistic.query_all_stock_industry_info()
    a_stock_list = []
    hk_stock_list = []
    other_stock_list = []
    for stock_name_code in stock_top_list:
        stock_code = stock_name_code[0].split('-', 1)[0]
        #path = 'other'
        if bool(re.search("^\d{5}$", stock_code)):
            #path = '港股'
            hk_stock_list.append(stock_name_code)
        elif bool(re.search("^\d{6}$", stock_code)):
            # 'A股/深证主板'、'A股/创业板'、'A股/上证主板'、'A股/科创板'
            a_condition = bool(re.search(
                "^(00(0|1|2|3)\d{3})|(30(0|1)\d{3})|(60(0|1|2|3|5)\d{3})|68(8|9)\d{3}$", stock_code))
            target_item = find_from_list_of_dict(
                all_a_stocks_industry_info_list, 'stock_code', stock_code)
            if a_condition and target_item:
                stock_name_code[1]['industry_name_first'] = target_item.get(
                    'industry_name_first')
                stock_name_code[1]['industry_name_second'] = target_item.get(
                    'industry_name_second')
                stock_name_code[1]['industry_name_third'] = target_item.get(
                    'industry_name_third')
                a_stock_list.append(stock_name_code)
            else:
                other_stock_list.append(stock_name_code)
        else:
            other_stock_list.append(stock_name_code)

    a_market = 'A股'
    hk_market = '港股'
    other_market = '其他'

    a_stock_compare_list = stocks_compare(
        a_stock_list, market=a_market, quarter_index=last_quarter_index, is_A_stock=True)
    hk_stock_compare_list = stocks_compare(
        hk_stock_list, market=hk_market, quarter_index=last_quarter_index,)
    other_stock_compare_list = stocks_compare(
        other_stock_list, market=other_market, quarter_index=last_quarter_index,)
    a_columns = [*columns, '三级行业', '二级行业', '一级行业']

    df_a_list = pd.DataFrame(a_stock_compare_list, columns=a_columns)
    df_hk_list = pd.DataFrame(hk_stock_compare_list, columns=columns)
    df_other_list = pd.DataFrame(other_stock_compare_list, columns=columns)

    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df_a_list.to_excel(writer, sheet_name=a_market)

    df_hk_list.to_excel(writer, sheet_name=hk_market)

    df_other_list.to_excel(writer, sheet_name=other_market)

    writer.save()


def all_stock_holder_detail(each_statistic=None, *, quarter_index=None, threshold=0):
    """ 所有股票的基金持仓细节
    Args:
        each_statistic (class): 统计类
        quarter_index (str, optional): 季度字符串. Defaults to None.
        threshold (int, optional): 输出门槛. Defaults to 0.
    """
    if each_statistic == None:
        each_statistic = FundStatistic()
    if quarter_index == None:
        quarter_index = get_last_quarter_str()
    stock_list = each_statistic.all_stock_fund_count_and_details(
        quarter_index=quarter_index,
        filter_count=threshold)
    for i in range(0, len(stock_list)):
        stock = stock_list[i]
        stock_name_code = stock[0]
        stock_code = stock_name_code.split('-', 1)[0]
        path = '其他'
        if bool(re.search("^\d{5}$", stock_code)):
            path = '港股'
        elif bool(re.search("^\d{6}$", stock_code)):
            if bool(re.search("^00(0|1|2|3)\d{3}$", stock_code)):
                path = 'A股/深证主板'
            elif bool(re.search("^30(0|1)\d{3}$", stock_code)):
                path = 'A股/创业板'
            elif bool(re.search("^60(0|1|2|3|5)\d{3}$", stock_code)):
                path = 'A股/上证主板'
            elif bool(re.search("^68(8|9)\d{3}$", stock_code)):
                path = 'A股/科创板'
            elif bool(re.search("^(8|4)(3|7)\d{4}$", stock_code)):
                path = 'A股/北交所'
            else:
                print('stock_name_code', stock_name_code)
        hold_fund_list = sorted(
            stock[1]['fund_list'], key=lambda x: x['持有市值(亿元)'], reverse=True)
        df_list = pd.DataFrame(hold_fund_list)
        stock_name_code = stock_name_code.replace('-*', '-').replace('/', '-')
        path = './outcome/数据整理/stocks/' + path + '/' + stock_name_code + '.xlsx'
        path = path.replace('\/', '-')
        update_xlsx_file(path, df_list, quarter_index)


def get_special_fund_code_holder_stock_detail(each_statistic=None, quarter_index=None):
    """获取某些基金的十大持仓股票信息
    """
    if each_statistic == None:
        each_statistic = FundStatistic()
    if quarter_index == None:
        quarter_index = get_last_quarter_str(1)
        print("quarter_index", quarter_index)
    holder_history_list = [
        {
            '001811': {
                'name': '中欧明睿新常态混合A',
                'radio': 0.2
            },
            '001705': {
                'name': '泓德战略转型股票',
                'radio': 0.2
            },
            '163415': {
                'name': '兴全商业模式优选混合',
                'radio': 0.2
            },
            '001043': {
                'name': '工银美丽城镇主题股票A',
                'radio': 0.1
            },
            '000547': {
                'name': '建信健康民生混合',
                'radio': 0.1
            },
            '450001': {
                'name': '国富中国收益混合',
                'radio': 0.2
            },
        },
        # """
        # 根据二季度高分基金池数据，以及近期组合表现，剔除一些不在高性价比基金池中基金，以及结合近期市场风格进行调仓以及调整成分基金比例。
        # 保留：中欧明睿新常态混合A(001811),建信健康民生混合(000547),
        # 调出：泓德战略转型股票(001705),兴全商业模式优选混合(163415),工银美丽城镇主题股票A(001043),国富中国收益混合(450001)
        # 调入：工银新金融股票（001054），工银瑞信战略转型主题股票A（000991），汇丰晋信动态策略混合A（540003）兴全绿色投资混合（163409）
        # 结合以上基金的近期表现，以及风控，以及维持整个组合均衡配置（目前组合偏科技板块）做出如上调整，欢迎大家跟调。
        # """
        {
            '001811': {
                'name': '中欧明睿新常态混合A',
                'radio': 0.2
            },
            '001054': {
                'name': '工银新金融股票',
                'radio': 0.2
            },
            '000991': {
                'name': '工银瑞信战略转型主题股票A',
                'radio': 0.1
            },
            '540003': {
                'name': '汇丰晋信动态策略混合A',
                'radio': 0.2
            },
            '000547': {
                'name': '建信健康民生混合',
                'radio': 0.1
            },
            '163409': {
                'name': '兴全绿色投资混合(LOF)',
                'radio': 0.2
            },
        },
        [
            {
                'code': '519002',
                'name': '华安安信消费混合',
                'radio': 0.2
            },
            {
                'code': '001718',
                'name': '工银瑞信物流产业股票',
                'radio': 0.2
            },
            {
                'code': '000991',
                'name': '工银瑞信战略转型主题股票A',
                'radio': 0.1
            },
            {
                'code': '540003',
                'name': '汇丰晋信动态策略混合A',
                'radio': 0.1
            },
            {
                'code': '450001',
                'name': '国富中国收益混合',
                'radio': 0.1
            },
            {
                'code': '000547',
                'name': '建信健康民生混合',
                'radio': 0.1
            },
            {
                'code': '163409',
                'name': '兴全绿色投资混合(LOF)',
                'radio': 0.2
            },
        ]
    ]
    # 基金组合信息
    fund_portfolio = holder_history_list[len(holder_history_list) - 1]
    fund_code_pool = [] #list(fund_portfolio.keys())
    for item in fund_portfolio:
        fund_code_pool.append(item.get('code'))
    print("fund_code_pool", fund_code_pool)
    holder_stock_industry_list = each_statistic.summary_special_funds_stock_detail(
        fund_code_pool, quarter_index)
    path = './outcome/数据整理/funds/高分权益基金组合十大持仓明细.xlsx'
    columns = ['基金代码', '基金名称', '基金类型', '基金经理', '基金总资产（亿元）', '基金股票总仓位',
               '十大股票仓位', '股票代码', '股票名称', '所占仓位', '所处仓位排名',  '三级行业', '二级行业', '一级行业']
    df_a_list = pd.DataFrame(holder_stock_industry_list, columns=columns)
    # print("df_a_list", df_a_list)

    update_xlsx_file_with_insert(path, df_a_list, sheet_name=quarter_index)

def compare(item1, item2):
    year1 = int(item1[0:4])
    quarter_index1 = int(item1[6:7])
    year2 = int(item2[0:4])
    quarter_index2 = int(item2[6:7])
    if year2 < year1 or (year2 == year1 and quarter_index2 < quarter_index1):
        return -1
    elif year2 > year1 or (year2 == year1 and quarter_index2 > quarter_index1):
        return 1
    else:
        return 0

# Calling
# list.sort(key=compare)
def calculate_quarter_fund_total():
    stock_markets = ['A股/上证主板', 'A股/创业板', 'A股/科创板', 'A股/深证主板', 'A股/北交所', '港股', '其他']
    for market in stock_markets:
        dir_path = './outcome/数据整理/stocks/' + market + '/'
        # dir_path = './outcome/数据整理/stocks/' + 'A股/北交所' + '/'
        files = read_dir_all_file(dir_path)
        print(market, "files", len(files))
        for file_path in files:
            path = dir_path + file_path
            xls = pd.ExcelFile(path, engine='openpyxl')
            quarter_list = []
            sum_column_name = '总计'
            sheet_names = []
            for sheet_name in xls.sheet_names:
                if sheet_name == sum_column_name:
                        continue
                sheet_names.append(sheet_name)
            sheet_names.sort(key=cmp_to_key(compare))
            for sheet_name in sheet_names:
                # if sheet_name == '总计':
                #     continue
                item_quarter_data = [sheet_name]
                df_cur_sheet = xls.parse(sheet_name)
                item_quarter_data.append(len(df_cur_sheet))
                item_quarter_data.append(
                    round(df_cur_sheet['持有市值(亿元)'].sum(), 2))
                quarter_list.append(item_quarter_data)
            columns = ["日期", "持有数量(只)", '持有市值(亿元)']
            df_quarter_list = pd.DataFrame(quarter_list, columns=columns)
            update_xlsx_file_with_sorted(path, df_quarter_list, sum_column_name, sheet_names)


if __name__ == '__main__':
    # 所有股票的基金持仓细节
    # all_stock_holder_detail(each_statistic)

    # 获取所有股票排名,按股票市场分类输出
    # all_stocks_rank(each_statistic)

    # 获取Top100股票排名
    # t100_stocks_rank(each_statistic=each_statistic)

    # 获取某些基金的十大持仓股票信息
    # get_special_fund_code_holder_stock_detail()

    calculate_quarter_fund_total()
    # select_condition_stocks_rank()
