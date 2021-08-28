'''
Desc: 一些基金策略，方案
File: /agree_strategy.py
Project: src
File Created: Monday, 24th May 2021 11:50:25 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from utils.index import get_last_quarter_str, update_xlsx_file
from sql_model.fund_query import FundQuery
import os
from pprint import pprint
import pandas as pd


def output_high_score_funds(each_query, quarter_index=None):
    """
    输出高分基金
    """
    if quarter_index == None:
        quarter_index = get_last_quarter_str()
    print("quarter_index", quarter_index)
    high_score_funds = each_query.select_high_score_funds(
        quarter_index=quarter_index)
    columns_bk = ['代码', '名称', '季度', '总资产', '现任基金经理管理起始时间', '投资风格', '三月最大回撤', '六月最大回撤', '夏普比率', '阿尔法系数', '贝塔系数',
                  'R平方', '标准差', '风险系数', '两年风险评级', '三年风险评级', '五年风险评级', '五年晨星评级', '三年晨星评级', '股票仓位', '十大持股仓位']
    columns = ['代码', '名称', '投资风格', '基金经理', '现任经理管理起始时间', '成立时间', '三年晨星评级', '五年晨星评级', '夏普比率', '股票仓位', '十大持股仓位',
               '两年风险评级', '三年风险评级', '五年风险评级', '阿尔法系数', '贝塔系数', '标准差', '总资产', '数据更新时间']
    df_high_score_funds = pd.DataFrame(high_score_funds, columns=columns)

    # pprint(df_high_score_funds)

    path = './outcome/数据整理/funds/high-score-funds.xlsx'
    update_xlsx_file(path, df_high_score_funds, quarter_index)


if __name__ == '__main__':
    each_query = FundQuery()
    output_high_score_funds(each_query)
