'''
Desc:
File: /query.py
Project: crud
File Created: Wednesday, 21st September 2022 10:54:27 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

import sys

sys.path.append('./src')
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.fund import FundBase, FundQuarter
from models.manager import ManagerAssoc
from models.var import engine

session = Session(engine)

def query_high_score_funds(quarter_index):
    words = ['%指数%', '%C', '%E', '%H%']
    rule = and_(*[FundBase.fund_name.notlike(w) for w in words])
    res =  session.query(FundQuarter,ManagerAssoc,FundBase).where(FundQuarter.fund_code == ManagerAssoc.fund_code).where(FundQuarter.fund_code == FundBase.fund_code).filter(FundQuarter.quarter_index == quarter_index, \
    FundQuarter.morning_star_rating_5 >= 3, # 5年评级大于等于3
    FundQuarter.morning_star_rating_3 == 5, # 3年评级等于5
    FundQuarter.stock_position_total >= 50, # 股票仓位大于50
    FundQuarter.stock_position_ten <= 60, # 十大股票仓位小于60
    FundQuarter.risk_assessment_sharpby > 1, # 夏普比例大于1
    FundQuarter.risk_rating_2 > 1, # 2年风险评级大于1
    FundQuarter.risk_rating_3 > 1, # 3年风险评级大于1
    FundQuarter.risk_rating_5 > 1, # 5年风险评级大于1
    # ManagerAssoc.manager_start_date < last_year_date, # 至少任职该基金一年
    FundQuarter.total_asset < 100, # 总规模资金小于100亿
    ).filter(rule).all()
    return res

def query_all_fund():
    all_funds = session.query(FundBase).all()
    all_fund_dict = {}
    for fund in all_funds:
        all_fund_dict[fund.fund_code] = {
            'fund_code': fund.fund_code,
            'morning_star_code': fund.morning_star_code,
            'fund_name': fund.fund_name,
            'fund_cat': fund.fund_cat,
        }
    return all_fund_dict

if __name__ == '__main__':
    quarter_index = '2022-Q2'
    fund_list = query_high_score_funds(quarter_index)
    # print("fund_list",fund_list)
    
