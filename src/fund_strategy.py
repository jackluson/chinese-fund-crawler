'''
Desc: 一些基金策略，方案
File: /agree_strategy.py
Project: src
File Created: Monday, 24th May 2021 11:50:25 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from sql_model.fund_query import FundQuery
import pandas as pd
from pprint import pprint

if __name__ == '__main__':
    each_query = FundQuery()
    high_score_funds = each_query.select_high_score_funds()
    columns = ['代码', '名称', '季度', '总资产', '起始时间', '投资风格', '三月最大回撤', '六月最大回撤', '夏普比率', '阿尔法系数', '贝塔系数',
               'R平方', '标准差', '风险系数', '两年风险评级', '三年风险评级', '五年风险评级', '五年晨星评级', '三年晨星评级', '股票仓位', '十大持股仓位']
    df_high_score_funds = pd.DataFrame(high_score_funds, columns=columns)

    pprint(df_high_score_funds)
    df_high_score_funds.to_excel(
        './output/xlsx/high-score-funds.xlsx', sheet_name='2021-Q1')
