'''
Desc: 基金数据的补充，更新
File: /supplement.py
Project: fund_info
File Created: Thursday, 3rd June 2021 3:19:21 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

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
      each_fund_update = FundUpdate()
      funds = fund_query.select_quarter_fund(0, 15000)
      print("funds's len", len(funds))
      for fund_item in funds:
        fund_code = fund_item[0]
        fund_api = FundApier(fund_code, platform='zh_fund')
        fund_api.get_analyse_info_zh()
        buy_status = fund_api.buy_status
        if buy_status == '已清盘' or buy_status == '终止上市' :
          each_fund_update.update_archive_status(1, fund_code=fund_code)
          continue
        print('没有归档基金状态:', fund_code, fund_api.buy_status, fund_api.sell_status)

    def update_fund_total_asset(self):
      fund_query = FundQuery()
      each_fund_update = FundUpdate()
    # 获取所有的A类基金
      all_total_asset_is_null_results = fund_query.select_total_asset_is_null()
      for fund_item in all_total_asset_is_null_results:
          fund_code = fund_item[0]
          platform = 'ai_fund'
          end_date = '2021-06-11'
          each_fund = FundApier(fund_code, end_date=end_date, platform=platform)

          total_asset = each_fund.get_total_asset()
              # 如果在爱基金平台找不到，则到展恒基金找
          if total_asset == None and platform == 'ai_fund':
              print("fund_code", fund_code)
              each_fund = FundApier(fund_code, end_date=end_date, platform='zh_fund')
              total_asset = each_fund.get_total_asset()
          if total_asset:
            each_fund_update.update_fund_total_asset(fund_code, total_asset)
