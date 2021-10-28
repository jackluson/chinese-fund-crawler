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
import os
import sys

sys.path.append('./src')

from src.acquire_fund_snapshot import get_fund_list


def main():
    input_value = input("请输入下列序号执行操作:\n \
        1.“快照” \n \
        2.“行业个股”\n \
        3.“股票日更”\n \
        4.“个股+日更”\n \
        5.“财务指标”\n \
        6.“A股估值”\n \
    输入：")
    if input_value == '1' or input_value == '快照':
        get_fund_list()  # 执行申万行业信息入库


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/crawler.log',  filemode='a', level=logging.INFO)
    main()
