'''
Desc: 获取晨星单支基金的基础信息 -- 代码，名称，分类基金公司，成立时间等这些基金一成立都不会变动的信息
File: /acquire_fund_base.py
Project: src
File Created: Monday, 8th March 2021 5:31:50 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import math
from utils import parse_cookiestr, set_cookies, login_site
from fund_info_crawler import FundInfo
from lib.mysnowflake import IdWorker
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
    chrome_driver = login()
    morning_cookies = chrome_driver.get_cookies()
    # 获取数据库的基金列表
    sql_count = "SELECT count(*)  FROM fund_morning_snapshot WHERE fund_code IS NOT NULL AND morning_star_code IS NOT NULL"
    cursor.execute(sql_count)
    count = cursor.fetchone()    # 获取记录条数
    print('count', count[0])

    IdWorker = IdWorker()
    page_limit = 10
    record_total = count[0]
    page_start = 3890
    error_funds = ['005086']  # 一些异常的基金详情页，如果发现记录该基金的code
    # 遍历从基金列表的单支基金
    while(page_start < record_total):
        sql = "SELECT fund_code, morning_star_code, fund_name FROM fund_morning_snapshot WHERE fund_code IS NOT NULL AND morning_star_code IS NOT NULL ORDER BY fund_code LIMIT %s, %s"
        cursor.execute(
            sql, [page_start, page_limit])    # 执行sql语句
        results = cursor.fetchall()    # 获取查询的所有记录
        for record in results:
            each_fund = FundInfo(
                record[0], record[1], record[2], chrome_driver, morning_cookies)
            # 从天天基金网上更新信息
            # each_fund.update_fund_info_by_tiantian()
            # 从晨星网上更新信息
            is_normal = each_fund.get_fund_detail_info()
            if is_normal == False or each_fund.found_date == '-':
                error_funds.append(each_fund.fund_code)
                continue
            # each_fund.get_asset_composition_info()
            # 拼接sql需要的数据
            snow_flake_id = IdWorker.get_id()
            base_dict = {
                'id': snow_flake_id,
                'fund_code': each_fund.fund_code,
                'morning_star_code': each_fund.morning_star_code,
                'fund_name': each_fund.fund_name,
                'fund_cat': each_fund.fund_cat,
                'company': each_fund.company,
                'found_date': each_fund.found_date
            }
            keys = ','.join(base_dict.keys())
            values = ','.join(['%s'] * len(base_dict))
            update_values = ''
            for key in base_dict.keys():
                if key in ['id', 'fund_code']:
                    continue
                update_values = update_values + '{0}=VALUES({0}),'.format(key)
            # 入库，不存在则创建，存在则更新
            base_sql_insert = "INSERT INTO {table} ({keys}) VALUES ({values})  ON DUPLICATE KEY UPDATE {update_values}; ".format(
                table='fund_morning_base',
                keys=keys,
                values=values,
                update_values=update_values[0:-1]
            )
            cursor.execute(base_sql_insert, tuple(base_dict.values()))
            connect.commit()
        page_start = page_start + page_limit
        print('page_start', page_start)
    chrome_driver.close()
    print('error_funds', error_funds)
