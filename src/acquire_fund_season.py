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
from utils import parse_cookiestr, set_cookies, login_site
from fund_info_crawler import FundSpider
from lib.mysnowflake import IdWorker
from time import sleep, time
import pymysql
import pandas
connect = pymysql.connect(host='127.0.0.1', user='root',
                          password='rootroot', db='fund_work', charset='utf8')
cursor = connect.cursor()
lock = Lock()


def login():
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(12000)
    login_url = 'https://www.morningstar.cn/membership/signin.aspx'
    lock.acquire()
    login_status = login_site(
        chrome_driver, login_url)
    lock.release()
    if login_status:
        print('login success')
    else:
        print('login fail')
        exit()
    return chrome_driver


if __name__ == '__main__':
    # 过滤没有股票持仓的基金
    sql_count = "SELECT COUNT(1) FROM fund_morning_base \
    LEFT JOIN fund_morning_snapshot ON fund_morning_snapshot.fund_code = fund_morning_base.fund_code \
    WHERE fund_morning_base.fund_cat NOT LIKE '%%货币%%' \
    AND fund_morning_base.fund_cat NOT LIKE '%%纯债基金%%' \
    AND fund_morning_base.fund_cat NOT LIKE '目标日期' \
    AND fund_morning_base.fund_cat NOT LIKE '%%短债基金%%'"
    cursor.execute(sql_count)
    count = cursor.fetchone()    # 获取记录条数
    print('count', count[0])
    IdWorker = IdWorker()
    page_limit = 5
    record_total = count[0]
    page_start = 0
    error_funds = []
    output_catch_head = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + \
        '类型' + ',' + '股票总仓位' + ',' + '页码' + ',' + '备注' + '\n'
    # 设置表头
    result_dir = './output/'

    if page_start == 0:
        with open(result_dir + 'fund_morning_season_catch.csv', 'w+') as csv_file:
            csv_file.write(output_catch_head)
    output_catch_error = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + \
        '类型' + ',' + '页码' + ',' + '备注' + '\n'
    if page_start == 0:
        with open(result_dir + 'fund_morning_season_error.csv', 'w+') as csv_file:
            csv_file.write(output_catch_error)
    df = pandas.read_csv(
        result_dir + 'fund_morning_season_error.csv', usecols=[0, 2, 4])
    fund_list = df.values.tolist()
    # print(len(d[d['代码'].astype(str).str.contains('10535')]))
    # print(df[df['代码'].astype(str).str.contains('10535')]
    #       ['股票总仓位'].values)

    def crawlData(start, end):
        chrome_driver = login()
        morning_cookies = chrome_driver.get_cookies()
        print('end', end)
        page_start = start
        page_limit = 10
        while(page_start < end):
            sql = "SELECT fund_morning_base.fund_code,\
            fund_morning_base.morning_star_code, fund_morning_base.fund_name, fund_morning_base.fund_cat, \
            fund_morning_snapshot.fund_rating_3,fund_morning_snapshot.fund_rating_5 \
            FROM fund_morning_base \
            LEFT JOIN fund_morning_snapshot ON fund_morning_snapshot.fund_code = fund_morning_base.fund_code \
            WHERE fund_morning_base.fund_cat NOT LIKE '%%货币%%' \
            AND fund_morning_base.fund_cat NOT LIKE '%%纯债基金%%' \
            AND fund_morning_base.fund_cat NOT LIKE '目标日期' \
            AND fund_morning_base.fund_cat NOT LIKE '%%短债基金%%' \
            ORDER BY fund_morning_snapshot.fund_rating_5 DESC,fund_morning_snapshot.fund_rating_3 DESC, \
            fund_morning_base.fund_cat, fund_morning_base.fund_code LIMIT %s, %s"
            lock.acquire()
            cursor.execute(
                sql, [page_start, page_limit])    # 执行sql语句
            results = cursor.fetchall()    # 获取查询的所有记录
            lock.release()
            for record in results:
                sleep(1)
                print(current_thread().getName(), 'record-->', record)
                each_fund = FundSpider(
                    record[0], record[1], record[2], chrome_driver, morning_cookies)
                is_normal = each_fund.go_fund_url()
                if is_normal == False:
                    lock.acquire()
                    error_funds.append(each_fund.fund_code)
                    fund_infos = [each_fund.fund_code, each_fund.morning_star_code,
                                  each_fund.fund_name, record[3], page_start, '页面跳转有问题']
                    with open(result_dir + 'fund_morning_season_error.csv', 'a') as csv_file:
                        output_line = ', '.join(str(x)
                                                for x in fund_infos) + '\n'
                        csv_file.write(output_line)
                    lock.release()
                    continue
                # each_fund.get_fund_manager_info()
                each_fund.get_fund_morning_rating()
                # each_fund.get_fund_season_info()
                continue
                if each_fund._is_trigger_catch == True:
                    lock.acquire()
                    fund_infos = [each_fund.fund_code, each_fund.morning_star_code,
                                  each_fund.fund_name, record[3],
                                  each_fund.stock_position['stock_total_position'],
                                  page_start, each_fund._catch_detail]
                    with open(result_dir + 'fund_morning_season_catch.csv', 'a') as csv_file:
                        output_line = ', '.join(str(x)
                                                for x in fund_infos) + '\n'
                        csv_file.write(output_line)
                    lock.release()
                fundDict = dict((name, getattr(each_fund, name))
                                for name in vars(each_fund)
                                if not (name.startswith('_') or getattr(each_fund, name) == None))

                # print(current_thread().getName(), fundDict)
            page_start = page_start + page_limit
            print(current_thread().getName(), 'page_start', page_start)
            sleep(3)
        chrome_driver.close()
    threaders = []
    start = time()
    step_num = 2500
    for i in range(1):
        print(i * step_num, (i+1) * step_num)
        t = Thread(target=crawlData, args=(
            i * step_num, (i+1) * step_num))
        t.setDaemon(True)
        threaders.append(t)
        t.start()
    for threader in threaders:
        threader.join()
    stop = time()
    print('run time is %s' % (stop-start))
    print('error_funds', error_funds)
    exit()
