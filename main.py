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


def main():
    input_value = input("请输入下列序号执行操作:\n \
        1.“快照” \n \
        2.“新基入库”\n \
        3.“季度信息”\n \
        4.“基金状态归档”\n \
    输入：")
    if input_value == '1' or input_value == '快照':
        page_index = 1
        get_fund_list(page_index)  # 执行申万行业信息入库
    elif input_value == '2' or input_value == '新基入库':
        acquire_fund_base()  # 执行行业股票信息入库
    elif input_value == '3' or input_value == "季度信息":
        acquire_fund_quarter()
    elif input_value == '4' or input_value == "基金状态归档":
        fund_supplement = FundSupplement()
        # 补充基金清算维度信息
        fund_supplement.update_archive_status()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/crawler.log',  filemode='a', level=logging.INFO)
    main()
