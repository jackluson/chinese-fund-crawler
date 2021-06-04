'''
Desc: 基金数据的补充，更新
File: /supplement.py
Project: fund_info
File Created: Thursday, 3rd June 2021 3:19:21 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import time
from utils.index import get_last_quarter_str
from sql_model.fund_query import FundQuery
from sql_model.fund_update import FundUpdate
from fund_info.api import FundApier

class FundSupplement:
    def __init__(self, code=None):
      self.fund_code = code
      # 动态计算季度信息
      self.quarter_index = get_last_quarter_str()
    
    def update_archive_status(self):
      fund_query = FundQuery()
      print("fund_query", fund_query)
      each_fund_update = FundUpdate()
      funds = fund_query.select_quarter_fund(0, 10000)
      for fund_item in funds:
        print("fund_item", fund_item)
        fund_code = fund_item[0]
        fund_api = FundApier(fund_code, platform='zh_fund')
        fund_api.get_analyse_info_zh()
        buy_status = fund_api.buy_status
        if buy_status == '已清盘':
          each_fund_update.update_archive_status(1, fund_code=fund_code)
          continue
        print('fund_api', fund_api.buy_status, fund_api.sell_status)
