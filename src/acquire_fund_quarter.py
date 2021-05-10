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
from fund_info.csv import FundCSV
from lib.mysnowflake import IdWorker
from utils.login import login_morning_star
from sql_model.fund_query import FundQuery

connect_instance = connect()
cursor = connect_instance.cursor()

lock = Lock()


def generate_insert_sql(target_dict, table_name, ignore_list):
    keys = ','.join(target_dict.keys())
    values = ','.join(['%s'] * len(target_dict))
    update_values = ''
    for key in target_dict.keys():
        if key in ignore_list:
            continue
        update_values = update_values + '{0}=VALUES({0}),'.format(key)
    sql_insert = "INSERT INTO {table} ({keys}) VALUES ({values})  ON DUPLICATE KEY UPDATE {update_values}; ".format(
        table=table_name,
        keys=keys,
        values=values,
        update_values=update_values[0:-1]
    )
    return sql_insert


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
    #     result_dir + 'fund_morning_season_error.csv', usecols=[0, 2, 4])
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
            print('results', results)
            for record in results:
                sleep(1)
                print(current_thread().getName(), 'record-->', record)
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
                quarter_index = each_fund.get_quarter_index()  # 数据更新时间
                if quarter_index == each_fund.quarter_index:
                    print('quarter_index', quarter_index)
                if each_fund.fund_name.endswith('A'):
                    print('fund_name', each_fund.fund_name[0:-1])
                    similar_name = each_fund.fund_name[0:-1]
                    results = each_fund_query.select_similar_fund(
                        similar_name)    # 获取查询的所有记录
                    print('results', results)
                each_fund.get_fund_season_info()  # 基本季度性数据
                each_fund.get_fund_manager_info()  # 基金经理模块
                each_fund.get_fund_morning_rating()  # 基金晨星评级
                each_fund.get_fund_qt_rating()  # 基金风险评级
                print('each_fund.total_asset', each_fund.total_asset)
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
                continue

                # 基金经理
                if each_fund.manager.get('id'):
                    manager_dict = {
                        'id': snow_flake_id,
                        'manager_id': each_fund.manager.get('id'),
                        'name': each_fund.manager.get('name'),
                        'brife': each_fund.manager.get('brife')
                    }
                    manager_sql_insert = generate_insert_sql(
                        manager_dict, 'fund_morning_manager', ['id', 'manager_id', 'name'])
                    lock.acquire()
                    # cursor.execute(manager_sql_insert,
                    #                tuple(manager_dict.values()))
                    # connect_instance.commit()
                    lock.release()
                # 季度信息  TODO: 对比数据更新时间field
                season_dict = {
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
                season_sql_insert = generate_insert_sql(
                    season_dict, 'fund_morning_season', ['id', 'quarter_index', 'fund_code'])
                lock.acquire()
                # cursor.execute(season_sql_insert,
                #                tuple(season_dict.values()))
                # connect_instance.commit()
                lock.release()
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
                    stock_sql_insert = generate_insert_sql(
                        stock_dict, 'fund_morning_stock_info', ['id', 'quarter_index', 'fund_code'])
                    lock.acquire()
                    # print('stock_sql_insert', stock_sql_insert)
                    # cursor.execute(stock_sql_insert,
                    #                tuple(stock_dict.values()))
                    # connect_instance.commit()
                    lock.release()
                # pprint(fundDict)
            page_start = page_start + page_limit
            print(current_thread().getName(), 'page_start', page_start)
            sleep(3)
        chrome_driver.close()
    threaders = []
    start_time = time()
    step_num = 10
    steps = [{
        "start": 800,
        "end": 2500
    }, {
        "start": 2740,
        "end": 5000
    }, {
        "start": 5100,
        "end": 7500
    }, {
        "start": 8300,
        "end": record_total
    }]
    for i in range(0):
        skip_num = 10
        # print(i * step_num + skip_num, (i+1) * step_num)
        # start = steps[i]['start']
        # end = steps[i]['end']
        start = i * step_num
        end = (i + 1) * step_num
        t = Thread(target=crawlData, args=(start, end))
        t.setDaemon(True)
        threaders.append(t)
        t.start()
    for threader in threaders:
        threader.join()
    end_time = time()
    print('run time is %s' % (end_time - start_time))
    # print('error_funds', error_funds)
    exit()
