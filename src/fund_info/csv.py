'''
Desc: 操作CSV
File: /csv.py
Project: fund_info
File Created: Monday, 10th May 2021 7:24:35 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from threading import Lock


class FundCSV:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.lock = Lock()

    # 爬取过程中异常基金
    def write_season_catch_fund(self, is_init=False, data=None):
        head_data = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + \
            '类型' + ',' + '股票总仓位' + ',' + '页码' + ',' + '备注' + '\n'
        mode = 'w+' if is_init else 'a'
        write_data = head_data if is_init else data
        self.lock.acquire()
        with open(self.output_dir + 'fund_morning_quarter_catch.csv', mode) as csv_file:
            csv_file.write(write_data)
        self.lock.release()

    # 基金url跳转异常基金
    def write_abnormal_url_fund(self, is_init=False, data=None):
        head_data = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + \
            '类型' + ',' + '页码' + ',' + '备注' + '\n'
        mode = 'w+' if is_init else 'a'
        write_data = head_data if is_init else data
        self.lock.acquire()
        with open(self.output_dir + 'fund_morning_quarter_abnormal.csv', mode) as csv_file:
            csv_file.write(write_data)
        self.lock.release()
