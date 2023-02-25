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

from pprint import pprint
from threading import Lock, current_thread
from time import sleep, time

from fund_info.api import FundApier
from fund_info.crawler import FundSpider
from fund_info.fund_csv import FundCSV
from lib.mysnowflake import IdWorker
from models.manager import Manager, ManagerAssoc
from sql_model.fund_insert import FundInsert
from sql_model.fund_query import FundQuery
from utils.driver import create_chrome_driver
from utils.index import bootstrap_thread
from utils.file_op import read_error_code_from_json, write_fund_json_data
from utils.login import login_morning_star

# 利用api获取同类基金的资产


def get_total_asset(fund_code, platform):
    each_fund = FundApier(fund_code, end_date='2021-05-07', platform=platform)
    total_asset = each_fund.get_total_asset()
    # 如果在爱基金平台找不到，则到展恒基金找
    if total_asset == None and platform != 'zh_fund':
        each_fund = FundApier(
            fund_code, end_date='2021-05-10', platform='zh_fund')
        total_asset = each_fund.get_total_asset()
    if total_asset == None and platform != 'ai_fund':
        each_fund = FundApier(
            fund_code, end_date='2021-05-10', platform='ai_fund')
        total_asset = each_fund.get_total_asset()
    return total_asset

def acquire_fund_quarter():
    lock = Lock()
    each_fund_query = FundQuery()
    idWorker = IdWorker()
    # result_dir = './output/'
    # fund_csv = FundCSV(result_dir)
    # fund_csv.write_season_catch_fund(True)
    # fund_csv.write_abnormal_url_fund(True)
    err_info = read_error_code_from_json()
    error_funds_with_page = err_info.get('error_funds_with_page')
    error_funds_with_found_date = err_info.get('error_funds_with_found_date')
    error_funds_with_unmatch = err_info.get('error_funds_with_unmatch')
    filename = err_info.get('filename')
    file_dir = err_info.get('file_dir')
    def crawlData(start, end):
        login_url = 'https://www.morningstar.cn/membership/signin.aspx'
        chrome_driver = create_chrome_driver()
        login_morning_star(chrome_driver, login_url, False)
        page_start = start
        page_limit = 10
        try:
            while(page_start < end):
                results = each_fund_query.select_quarter_fund(
                    page_start, page_limit)
                for record in results:
                    fund_code = record[0]
                    if fund_code in error_funds_with_page or fund_code in error_funds_with_found_date or fund_code in error_funds_with_unmatch:
                        print('exist error fund: ', fund_code)
                        continue
                    each_fund = FundSpider(fund_code, record[1], record[2], chrome_driver)
                    each_fund.set_found_data(record[3])
                    is_error_page = each_fund.go_fund_url()
                    # 是否能正常跳转到基金详情页，没有的话，写入csv,退出当前循环
                    if is_error_page == True:
                        # error_funds.append(each_fund.fund_code)
                        # fund_infos = [each_fund.fund_code, each_fund.morning_star_code,
                        #             each_fund.fund_name, record[3], page_start, '页面跳转有问题']
                        # output_line = ', '.join(str(x)
                        #                         for x in fund_infos) + '\n'
                        # fund_csv.write_abnormal_url_fund(False, output_line)
                        error_funds_with_page.append(each_fund.fund_code)

                        continue
                    # 开始爬取数据
                    quarter_index = each_fund.get_quarter_index()  # 数据更新时间,如果不一致，不爬取下面数据
                    if quarter_index != each_fund.quarter_index:
                        # print('quarter_index', quarter_index, each_fund.update_date,
                        #     each_fund.fund_code, each_fund.fund_name)
                        error_funds_with_unmatch.append(each_fund.fund_code)
                        continue

                    each_fund.get_fund_season_info()  # 基本季度性数据
                    each_fund.get_fund_manager_info()  # 基金经理模块
                    each_fund.get_fund_morning_rating()  # 基金晨星评级
                    each_fund.get_fund_qt_rating()  # 基金风险评级
                    # 判断是否有股票持仓，有则爬取
                    if each_fund.stock_position['total'] != '0.00' and each_fund.total_asset != None:
                        each_fund.get_asset_composition_info()
                    # 爬取过程中是否有异常,有的话，存在csv中
                    # if each_fund._is_trigger_catch == True:
                    #     fund_infos = [each_fund.fund_code, each_fund.morning_star_code,
                    #                 each_fund.fund_name, record[3],
                    #                 each_fund.stock_position['total'],
                    #                 page_start, each_fund._catch_detail]
                    #     output_line = ', '.join(str(x)
                    #                             for x in fund_infos) + '\n'
                    #     fund_csv.write_season_catch_fund(False, output_line)
                    # 入库
                    lock.acquire()
                    snow_flake_id = idWorker.get_id()
                    lock.release()
                    # 开始存入数据
                    fund_insert = FundInsert()
                    # 基金经理
                    first_manager_id = None
                    first_manager_start_date = None
                    for manager_item in each_fund.manager_list:
                        manager = Manager(**manager_item)
                        manager.upsert()
                        if first_manager_id == None:
                            first_manager_id = manager_item['manager_id']
                        if first_manager_start_date == None:
                            first_manager_start_date = manager_item['manager_start_date']
                        manager_assoc_data = {
                            'quarter_index': quarter_index,
                            'manager_start_date': manager_item['manager_start_date'],
                            'manager_id': manager_item['manager_id'],
                            'fund_code': each_fund.fund_code
                        }
                        manager_assoc = ManagerAssoc(**manager_assoc_data)
                        manager_assoc.upsert()
                        # fund_insert.insert_fund_manger_info(manager_dict)
                    init_total_asset = each_fund.total_asset
                    quarterly_dict = {
                        # 'id': snow_flake_id,
                        'quarter_index': each_fund.quarter_index,
                        'fund_code': each_fund.fund_code,
                        'investname_style': each_fund.investname_style,
                        # 'total_asset': each_fund.total_asset,
                        'manager_id': first_manager_id, # 暂时存第一个基金经理信息
                        'manager_start_date': first_manager_start_date,  # 暂时存第一个基金经理信息
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
                    # 获取同类基金，再获取同类基金的总资产
                    if each_fund.fund_name.endswith('A') or each_fund.fund_name.endswith('B') or each_fund.fund_name.endswith('C'):
                        similar_name = each_fund.fund_name[0:-1]
                        similar_results = each_fund_query.select_similar_fund(
                            similar_name)    # 获取查询的所有记录
                        # platform = 'zh_fund' if '封闭' in similar_name else 'ai_fund'
                        platform = 'danjuan'
                        for i in range(0, len(similar_results)):
                            item = similar_results[i]
                            item_code = item[0]
                            if item_code == each_fund.fund_code:
                                continue
                            total_asset = get_total_asset(item_code, platform)
                            if total_asset != None:
                                init_total_asset = init_total_asset - total_asset
                            else:
                                print("total_asset is None", item_code, item[2])
                            for manager_item in each_fund.manager_list:
                                manager_assoc_data = {
                                    'quarter_index': quarter_index,
                                    'manager_start_date': manager_item['manager_start_date'],
                                    'manager_id': manager_item['manager_id'],
                                    'fund_code': item_code
                                }
                                manager_assoc = ManagerAssoc(**manager_assoc_data)
                                manager_assoc.upsert()
                            quarterly_dict['fund_code'] = item_code
                            quarterly_dict['total_asset'] = total_asset
                            quarterly_dict['id'] = snow_flake_id + i + 1
                            # 入库
                            fund_insert.fund_quarterly_info(quarterly_dict)
                            if float(stock_position_total) > 0:
                                stock_dict['fund_code'] = item_code
                                stock_dict['id'] = snow_flake_id + i + 1
                                # 入库
                                fund_insert.fund_stock_info(stock_dict)
                    quarterly_dict['fund_code'] = each_fund.fund_code
                    quarterly_dict['total_asset'] = init_total_asset
                    quarterly_dict['id'] = snow_flake_id
                    fund_insert.fund_quarterly_info(quarterly_dict)
                    if float(stock_position_total) > 0:
                        stock_dict['fund_code'] = each_fund.fund_code
                        stock_dict['id'] = snow_flake_id
                        fund_insert.fund_stock_info(stock_dict)
                    # pprint(fundDict)
                page_start = page_start + page_limit
                print(current_thread().getName(), 'page_start', page_start)
                sleep(3)
        except(BaseException):
            chrome_driver.close()
            raise BaseException
        chrome_driver.close()
    thread_count = 6
    total_start_time = time()
    # record_total = each_fund_query.select_quarter_fund_total()    # 获取记录条数
    # bootstrap_thread(crawlData, record_total, thread_count)
    record_total = each_fund_query.select_quarter_fund_total()    # 获取记录条数
    for i in range(2):
        start_time = time()
        print('record_total', record_total)
        try:
            bootstrap_thread(crawlData, record_total, thread_count)
        except:
            cur_total = each_fund_query.select_quarter_fund_total()    # 获取记录条数
            print('crawler item count:', record_total - cur_total)
            record_total = cur_total
        end_time = time()
        print("耗时: {:.2f}秒".format(end_time - start_time))
    write_fund_json_data({'error_funds_with_page': error_funds_with_page, 'error_funds_with_found_date': error_funds_with_found_date, 'error_funds_with_unmatch': error_funds_with_unmatch}, filename=filename, file_dir=file_dir)
    total_end_time = time()
    print("total耗时: {:.2f}秒".format(total_end_time - total_start_time))
    exit()

if __name__ == '__main__':
    acquire_fund_quarter()
