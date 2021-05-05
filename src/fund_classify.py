'''
Desc: 纠正基金BC类的总资产
File: /fund_classify.py
File Created: Tuesday, 4th May 2021 12:39:10 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from pprint import pprint
from db.connect import connect
from time import sleep
import os
from fund_info_api import FundApier

connect_instance = connect()
cursor = connect_instance.cursor()

if __name__ == '__main__':
    page_start = 3000
    page_limit = 10000
    sql_query_a_class = "SELECT fund_code, SUBSTRING(fund_name, 1, CHAR_LENGTH(fund_name)-1) as name, fund_name FROM fund_morning_base WHERE fund_name LIKE '%%A' LIMIT %s, %s ;"
    cursor.execute(sql_query_a_class, [page_start, page_limit])    # 执行sql语句
    all_a_results = cursor.fetchall()    # 获取查询的所有记录
    for i in range(0, len(all_a_results)):
        # pprint(result[1])
        result = all_a_results[i]
        sql_query_b_class = "SELECT fund_code, fund_name FROM fund_morning_base WHERE fund_name LIKE '" + \
            result[1] + "C';"
        # print('sql_query_b_class', sql_query_b_class)
        cursor.execute(sql_query_b_class)
        c_class_result = cursor.fetchone()
        if c_class_result:
            fund_code = c_class_result[0]
            fund_name = c_class_result[1]
            if '封闭' in fund_name:
                pprint(c_class_result)
            else:
                each_fund = FundApier(fund_code)
                each_fund.get_base_info()
                total_asset = each_fund.total_asset
                sql_update = "UPDATE fund_morning_quarter SET total_asset = %s WHERE fund_code = %s;"
                cursor.execute(sql_update, [total_asset, fund_code])
                connect_instance.commit()
