'''
Desc: 获取晨星单支基金的基础信息 -- 代码，名称，分类基金公司，成立时间等这些基金一成立都不会变动的信息
File: /acquire_fund_base.py
Project: src
File Created: Monday, 8th March 2021 5:31:50 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''
import os
import math
from utils.login import login_morning_star
from fund_info.crawler import FundSpider
from lib.mysnowflake import IdWorker
import pymysql
from db.connect import connect

connect_instance = connect()
cursor = connect_instance.cursor()


if __name__ == '__main__':

    # 获取数据库的基金列表
    env_snapshot_table_name = os.getenv('snapshot_table_name')
    sql_count = "SELECT count(*) FROM " + env_snapshot_table_name + \
        " WHERE fund_code NOT IN (SELECT fund_code FROM fund_morning_base);"
    cursor.execute(sql_count)
    count = cursor.fetchone()    # 获取记录条数
    print('count', count[0])
    login_url = 'https://www.morningstar.cn/membership/signin.aspx'
    chrome_driver = login_morning_star(login_url, True)
    IdWorker = IdWorker()
    page_limit = 10
    record_total = count[0]
    page_start = 0
    error_funds = []  # 一些异常的基金详情页，如果发现记录该基金的code
    # 遍历从基金列表的单支基金
    while(page_start < record_total):
        # 从fund_morning_snapshot_2021_q1 查出 fund_morning_base 中不存在的基金
        sql = "SELECT fund_code, morning_star_code, fund_name FROM " + env_snapshot_table_name + \
            " WHERE fund_code NOT IN (SELECT fund_code FROM fund_morning_base) ORDER BY fund_code LIMIT %s, %s"
        cursor.execute(
            sql, [page_start, page_limit])    # 执行sql语句
        results = cursor.fetchall()    # 获取查询的所有记录
        for record in results:
            each_fund = FundSpider(
                record[0], record[1], record[2], chrome_driver)
            # 从晨星网上更新信息
            is_normal = each_fund.go_fund_url()
            if is_normal == False:
                error_funds.append(each_fund.fund_code)
                continue
            each_fund.get_fund_base_info()
            # 去掉没有成立时间的
            if each_fund.found_date == '-':
                error_funds.append(each_fund.fund_code)
                continue
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
            base_sql_insert = "INSERT INTO {table} ({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE {update_values}; ".format(
                table='fund_morning_base',
                keys=keys,
                values=values,
                update_values=update_values[0:-1]
            )
            cursor.execute(base_sql_insert, tuple(base_dict.values()))
            connect_instance.commit()
        page_start = page_start + page_limit
        print('page_start', page_start)
    chrome_driver.close()
    print('error_funds', error_funds)
