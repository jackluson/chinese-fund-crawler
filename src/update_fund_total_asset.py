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
from sql_model.fund_query import FundQuery
from fund_info.api import FundApier


if __name__ == '__main__':
    page_start = 3600
    page_limit = 10000
    fund_query = FundQuery()
    # 获取所有的A类基金
    all_a_results = fund_query.select_all_a_class_fund(
        page_start, page_limit)    # 获取查询的所有记录
    for i in range(0, len(all_a_results)):
        # pprint(result[1])
        name = all_a_results[i]
        c_class_result = fund_query.select_c_class_fund(name[1])
        if c_class_result:
            fund_code = c_class_result[0]
            fund_name = c_class_result[1]
            platform = 'zh_fund' if '封闭' in fund_name else 'ai_fund'
            each_fund = FundApier(fund_code, end_date='2021-05-07', platform=platform)

            total_asset = each_fund.get_total_asset()
            # 如果在爱基金平台找不到，则到展恒基金找
            if total_asset == None and platform == 'ai_fund':
                print("fund_code", i, fund_name, fund_code)
                each_fund = FundApier(fund_code, end_date='2021-05-07', platform='zh_fund')
                total_asset = each_fund.get_total_asset()

            fund_query.update_fund_total_asset(fund_code, total_asset)
