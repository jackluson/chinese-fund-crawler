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
from utils import parse_cookiestr, set_cookies, login_site
from IOFile import read_group_fund_json, read_chenxingcode_json
from FundParameterInfo import FundInfo
from lib.mysnowflake import IdWorker
from time import sleep
import pymysql
connect = pymysql.connect(host='127.0.0.1', user='root',
                          password='xxxx', db='fund_work', charset='utf8')
cursor = connect.cursor()


def login():
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(12000)
    login_url = 'https://www.morningstar.cn/membership/signin.aspx'
    login_status = login_site(
        chrome_driver, login_url)
    if login_status:
        print('login success')
    else:
        print('login fail')
        exit()
    return chrome_driver


if __name__ == '__main__':
    # chrome_driver = login()
    # morning_cookies = chrome_driver.get_cookies()
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
    page_limit = 20
    record_total = count[0]
    page_start = 1
    error_funds = []
    while(page_start < record_total):
        sql = "SELECT fund_morning_base.fund_code,\
        fund_morning_base.fund_name, fund_morning_base.fund_cat, fund_morning_base.morning_star_code, \
        fund_morning_snapshot.fund_rating_3,fund_morning_snapshot.fund_rating_5 \
        FROM fund_morning_base \
        LEFT JOIN fund_morning_snapshot ON fund_morning_snapshot.fund_code = fund_morning_base.fund_code \
        WHERE fund_morning_base.fund_cat NOT LIKE '%%货币%%' \
        AND fund_morning_base.fund_cat NOT LIKE '%%纯债基金%%' \
        AND fund_morning_base.fund_cat NOT LIKE '目标日期' \
        AND fund_morning_base.fund_cat NOT LIKE '%%短债基金%%' \
        ORDER BY fund_morning_snapshot.fund_rating_5 DESC,fund_morning_snapshot.fund_rating_3 DESC, \
        fund_morning_base.fund_cat, fund_morning_base.fund_code LIMIT %s, %s"
        cursor.execute(
            sql, [page_start, page_limit])    # 执行sql语句
        results = cursor.fetchall()    # 获取查询的所有记录
        for record in results:
            print('record', record)
            continue
            each_fund = FundInfo(
                record[0], record[1], record[2], 1, 1)

            # fund_list.append(each_fund)
        page_start = page_start + page_limit
        print('page_start', page_start)
        sleep(3)
    chrome_driver.close()
    print('error_funds', error_funds)
    exit()
