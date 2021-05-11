# -*- coding:UTF-8 -*-
'''
Desc: 获取晨星单支基金的基金季度变动信息 -- 股票持仓比例，十大持仓，基金经理，一些风险指标
File: /export_fund_advanced.py
Project: src
File Created: Wednesday, 10th March 2021 8:56:58 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import math
from threading import Thread, Lock, current_thread
from time import sleep, time
from pprint import pprint
import pandas
from db.connect import connect
from fund_info.crawler import FundSpider
from fund_info.api import FundApier
from fund_info.csv import FundCSV
from lib.mysnowflake import IdWorker
from utils.login import login_morning_star
from sql_model.fund_query import FundQuery
from sql_model.fund_insert import FundInsert

connect_instance = connect()
cursor = connect_instance.cursor()

lock = Lock()

# 利用api获取同类基金的资产


def get_total_asset(fund_code, platform):
    each_fund = FundApier(fund_code, '2021-05-07', platform)
    total_asset = each_fund.get_total_asset()
    # 如果在爱基金平台找不到，则到展恒基金找
    if total_asset == None and platform == 'ai_fund':
        print("fund_code", total_asset, fund_code)
        each_fund = FundApier(fund_code, '2021-05-10', 'zh_fund')
        total_asset = each_fund.get_total_asset()


if __name__ == '__main__':

    each_fund_query = FundQuery()

    record_total = each_fund_query.get_crawler_quarter_fund_total()    # 获取记录条数
    IdWorker = IdWorker()
    page_limit = 5
    page_start = 0
    # error_funds = []
    # 设置表头
    result_dir = './output/'
    fund_csv = FundCSV(result_dir)

    if page_start == 0:
        fund_csv.write_season_catch_fund(True)
        fund_csv.write_abnormal_url_fund(True)

    # df = pandas.read_csv(
    #     result_dir + 'fund_morning_quarter_error.csv', usecols=[0, 2, 4])
    # fund_list = df.values.tolist()
    # print(len(d[d['代码'].astype(str).str.contains('10535')]))
    # print(df[df['代码'].astype(str).str.contains('10535')]
    #       ['股票总仓位'].values)

    def crawlData(start, end):
        login_url = 'https://www.morningstar.cn/membership/signin.aspx'
        chrome_driver = login_morning_star(login_url, True)
        page_start = start
        page_limit = 10
        while(page_start < end):
            results = each_fund_query.select_quarter_fund(
                page_start, page_limit)
            for record in results:
                sleep(1)
                each_fund = FundSpider(
                    record[0], record[1], record[2], chrome_driver)
                is_normal = each_fund.go_fund_url()
                # 是否能正常跳转到基金详情页，没有的话，写入csv,退出当前循环
                if is_normal == False:
                    # error_funds.append(each_fund.fund_code)
                    fund_infos = [each_fund.fund_code, each_fund.morning_star_code,
                                  each_fund.fund_name, record[3], page_start, '页面跳转有问题']
                    output_line = ', '.join(str(x)
                                            for x in fund_infos) + '\n'
                    fund_csv.write_abnormal_url_fund(False, output_line)

                    continue
                # 开始爬取数据
                quarter_index = each_fund.get_quarter_index()  # 数据更新时间,如果不一致，不爬取下面数据
                if quarter_index != each_fund.quarter_index:
                    print('quarter_index', quarter_index)
                    continue

                each_fund.get_fund_season_info()  # 基本季度性数据
                each_fund.get_fund_manager_info()  # 基金经理模块
                each_fund.get_fund_morning_rating()  # 基金晨星评级
                each_fund.get_fund_qt_rating()  # 基金风险评级
                # 判断是否有股票持仓，有则爬取
                if each_fund.stock_position['total'] != '0.00' and each_fund.total_asset != None:
                    each_fund.get_asset_composition_info()
                # 爬取过程中是否有异常,有的话，存在csv中
                if each_fund._is_trigger_catch == True:
                    fund_infos = [each_fund.fund_code, each_fund.morning_star_code,
                                  each_fund.fund_name, record[3],
                                  each_fund.stock_position['total'],
                                  page_start, each_fund._catch_detail]
                    fund_csv.write_season_catch_fund(False, output_line)
                # 入库
                lock.acquire()
                snow_flake_id = IdWorker.get_id()
                lock.release()
                # 开始存入数据
                fund_insert = FundInsert()
                # 基金经理
                if each_fund.manager.get('id'):
                    manager_dict = {
                        'id': snow_flake_id,
                        'manager_id': each_fund.manager.get('id'),
                        'name': each_fund.manager.get('name'),
                        'brife': each_fund.manager.get('brife')
                    }
                    fund_insert.insert_fund_manger_info(manager_dict)
                # 季度信息  TODO: 对比数据更新时间field
                quarterly_dict = {
                    'id': snow_flake_id,
                    'quarter_index': each_fund.quarter_index,
                    'fund_code': each_fund.fund_code,
                    'investname_style': each_fund.investname_style,
                    'total_asset': each_fund.total_asset,
                    'manager_id': each_fund.manager.get('id'),
                    'manager_start_date': each_fund.manager.get('start_date'),
                    'three_month_retracement': each_fund.three_month_retracement,
                    'june_month_retracement': each_fund.june_month_retracement,
                    'risk_statistics_alpha': each_fund.risk_statistics.get('alpha'),
                    'risk_statistics_beta': each_fund.risk_statistics.get('beta'),
                    'risk_statistics_r_square': each_fund.risk_statistics.get('r_square'),
                    'risk_assessment_standard_deviation': each_fund.risk_assessment.get('standard_deviation'),
                    'risk_assessment_risk_coefficient': each_fund.risk_assessment.get('risk_coefficient'),
                    'risk_assessment_sharpby': each_fund.risk_assessment.get('sharpby'),
                    'risk_rating_2': each_fund.risk_rating.get(2),
                    'risk_rating_3': each_fund.risk_rating.get(3),
                    'risk_rating_5': each_fund.risk_rating.get(5),
                    'risk_rating_10': each_fund.risk_rating.get(10),
                    'stock_position_total': each_fund.stock_position.get('total'),
                    'stock_position_ten': each_fund.stock_position.get('ten'),
                    'bond_position_total': each_fund.bond_position.get('total'),
                    'bond_position_five': each_fund.bond_position.get('five'),
                    'morning_star_rating_3': each_fund.morning_star_rating.get(3),
                    'morning_star_rating_5': each_fund.morning_star_rating.get(5),
                    'morning_star_rating_10': each_fund.morning_star_rating.get(10),
                }
                fund_insert.fund_quarterly_info(quarterly_dict)
                # 入库十大股票持仓
                stock_position_total = each_fund.stock_position.get(
                    'total', '0.00')
                if float(stock_position_total) > 0:
                    stock_dict = {
                        'id': snow_flake_id,
                        'quarter_index': each_fund.quarter_index,
                        'fund_code': each_fund.fund_code,
                        'stock_position_total': each_fund.stock_position.get('total'),
                    }
                    for index in range(len(each_fund.ten_top_stock_list)):
                        temp_stock = each_fund.ten_top_stock_list[index]
                        prefix = 'top_stock_' + str(index) + '_'
                        code_key = prefix + 'code'
                        stock_dict[code_key] = temp_stock['stock_code']
                        name_key = prefix + 'name'
                        stock_dict[name_key] = temp_stock['stock_name']
                        portion_key = prefix + 'portion'
                        stock_dict[portion_key] = temp_stock['stock_portion']
                        market_key = prefix + 'market'
                        stock_dict[market_key] = temp_stock['stock_market']
                    fund_insert.fund_stock_info(stock_dict)
                # 获取同类基金，再获取同类基金的总资产
                if each_fund.fund_name.endswith('A'):
                    similar_name = each_fund.fund_name[0:-1]
                    results = each_fund_query.select_similar_fund(
                        similar_name)    # 获取查询的所有记录
                    platform = 'zh_fund' if '封闭' in similar_name else 'ai_fund'
                    for i in range(0, len(results)):
                        item = results[i]
                        item_code = item[0]
                        total_asset = get_total_asset(item_code, platform)
                        quarterly_dict['fund_code'] = item_code
                        quarterly_dict['total_asset'] = total_asset
                        quarterly_dict['id'] = snow_flake_id + i + 1
                        fund_insert.fund_quarterly_info(quarterly_dict)
                        stock_dict['fund_code'] = item_code
                        stock_dict['id'] = snow_flake_id + i + 1
                        fund_insert.fund_stock_info(stock_dict)
                # pprint(fundDict)
            page_start = page_start + page_limit
            print(current_thread().getName(), 'page_start', page_start)
            sleep(3)
        chrome_driver.close()
    threaders = []
    start_time = time()
    step_num = 10
    steps = [{
        "start": 0,
        "end": 1500
    }, {
        "start": 1500,
        "end": 3000
    }, {
        "start": 3000,
        "end": 4500
    }, {
        "start": 4500,
        "end": record_total
    }]
    for i in range(4):
        skip_num = 0
        # print(i * step_num + skip_num, (i + 1) * step_num)
        start = steps[i]['start']
        end = steps[i]['end']
        # start = i * step_num
        # end = (i + 1) * step_num
        t = Thread(target=crawlData, args=(start, end))
        t.setDaemon(True)
        threaders.append(t)
        t.start()
    for threader in threaders:
        threader.join()
    end_time = time()
    print(record_total, 'run time is %s' % (end_time - start_time))
    # print('error_funds', error_funds)
    exit()
