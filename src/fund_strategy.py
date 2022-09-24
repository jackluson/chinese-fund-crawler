'''
Desc: 一些基金策略，方案
File: /agree_strategy.py
Project: src
File Created: Monday, 24th May 2021 11:50:25 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from datetime import timedelta, date
from utils.index import get_last_quarter_str, update_xlsx_file_with_insert
from crud.query import query_high_score_funds
import pandas as pd

def output_high_score_funds(quarter_index=None):
    """
    输出高分基金
    """
    if quarter_index == None:
        quarter_index = get_last_quarter_str()
    print("quarter_index", quarter_index)
    fund_list = query_high_score_funds(quarter_index)
    funds_map = {}
    for fund in fund_list:
        fund_code = fund[0].fund_code
        exist_fund = funds_map.get(fund_code)
        if exist_fund:
            exist_fund.append(fund)
            funds_map[fund_code] = exist_fund
        else:
            funds_map[fund_code] = [fund]
    high_score_funds = []
    delta = timedelta(days=1 * 365)
    date_now = date.today()
    for fund_code, funds in funds_map.items():
        fund_info = []
        is_meet_manager_start_date = False
        is_super_one = False
        for fund_item in funds:
            if is_meet_manager_start_date == False and date_now - delta > fund_item[1].manager_start_date:
                is_meet_manager_start_date = True
            if is_super_one == True:
                fund_info[3] =  fund_info[3] + ",\n" + fund_item[1].manager.name
                manager_start_date = fund_item[1].manager_start_date.strftime('%Y-%m-%d')
                fund_info[4] =  fund_info[4] + ",\n" + manager_start_date
            else:
                is_super_one = True
                fund_info.append(fund_item[0].fund_code)
                fund_info.append(fund_item[0].fund.fund_name)
                fund_info.append(fund_item[0].investname_style)
                fund_info.append(fund_item[1].manager.name)
                manager_start_date = fund_item[1].manager_start_date.strftime('%Y-%m-%d')
                fund_info.append(manager_start_date)
                fund_info.append(fund_item[0].fund.found_date)
                fund_info.append(fund_item[0].morning_star_rating_3)
                fund_info.append(fund_item[0].morning_star_rating_5)
                fund_info.append(fund_item[0].risk_assessment_sharpby)
                fund_info.append(fund_item[0].stock_position_total)
                fund_info.append(fund_item[0].stock_position_ten)
                fund_info.append(fund_item[0].risk_rating_2)
                fund_info.append(fund_item[0].risk_rating_3)
                fund_info.append(fund_item[0].risk_rating_5)
                fund_info.append(fund_item[0].risk_statistics_alpha)
                fund_info.append(fund_item[0].risk_statistics_beta)
                fund_info.append(fund_item[0].risk_assessment_standard_deviation)
                fund_info.append(fund_item[0].total_asset)
                fund_info.append(fund_item[0].quarter_index)
        if is_meet_manager_start_date:
            high_score_funds.append(fund_info)
    columns = ['代码', '名称', '投资风格', '基金经理', '现任经理管理起始时间', '成立时间', '三年晨星评级', '五年晨星评级', '夏普比率', '股票仓位', '十大持股仓位',
               '两年风险评级', '三年风险评级', '五年风险评级', '阿尔法系数', '贝塔系数', '标准差', '总资产', '数据更新时间']
    df_high_score_funds = pd.DataFrame(high_score_funds, columns=columns)
    # pprint(df_high_score_funds)
    path = './outcome/数据整理/funds/high-score-funds.xlsx'
    update_xlsx_file_with_insert(path, df_high_score_funds, quarter_index)


if __name__ == '__main__':
    output_high_score_funds()
