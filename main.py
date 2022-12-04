'''
Desc:
File: /main.py
Project: fund-morning-star-crawler
File Created: Thursday, 28th October 2021 10:51:07 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import logging
import sys

sys.path.append('./src')

from src.acquire_fund_snapshot import get_fund_list
from src.acquire_fund_base import acquire_fund_base
from src.fund_info.supplement import FundSupplement
from src.acquire_fund_quarter import acquire_fund_quarter
from src.acquire_fund_snapshot import get_fund_list
from src.fund_info_supplement import update_fund_archive_status
from src.fund_statistic import (all_stock_holder_detail, all_stocks_rank,
                                calculate_quarter_fund_total,
                                get_combination_holder_stock_detail,
                                t100_stocks_rank)
from src.fund_strategy import output_high_score_funds
from src.sync_fund_base import further_complete_base_info, sync_fund_base


def main():
    input_value = input("Please enter the following serial number to perform the operation:\n \
        1.“Snapshot” \n \
        2.“New base storage”\n \
        3.“Snapshot Sync New Base”\n \
        4.“Supplementary Fund Basic Data”\n \
        5.“Fund Status Archive”\n \
        6.“Quarter Information”\n \
        7.“Ranking of Fund Holdings”\n \
        8.“Top 100 Awkward Fund Stocks”\n \
        9. ”Stock holding fund details”\n \
        10.”Summary of stock holding funds”\n \
        11.”High Score Fund” \n  \
        12.”Composite position details” \n  \
    输入：")
    if input_value == '1':
        page_index = 1
        get_fund_list(page_index)  # 执行申万行业信息入库
    elif input_value == '2':
        acquire_fund_base()  # 执行行业股票信息入库
    elif input_value == '3':
        page_index = 1
        sync_fund_base(page_index)
    elif input_value == '4':
        further_complete_base_info()
    elif input_value == '5':
        update_fund_archive_status()
    elif input_value == '6':
        acquire_fund_quarter()
    elif input_value == '7':
        all_stocks_rank()
    elif input_value == '8':
        t100_stocks_rank()
    elif input_value == '9':
        all_stock_holder_detail()
    elif input_value == '10':
        calculate_quarter_fund_total()
    elif input_value == '11':
        output_high_score_funds()
    else:
        print('输入有误')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/crawler.log',  filemode='a', level=logging.INFO)
    main()
