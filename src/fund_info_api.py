'''
Desc: 从基金平台api获取基金信息
File: /fund_info_api.py
File Created: Wednesday, 5th May 2021 4:17:44 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import requests
import json
import time
import os
from pprint import pprint
from utils import write_json_data


class FundApier:
    def __init__(self, code):
        self.fund_code = code
        self.cur_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        self.end_date = '2021-04-30'
        self.total_asset = None
        file_dir = os.getcwd() + '/output/json/' + self.cur_date + '/'
        self.file_path = '{file_dir}{fund_code}-{end_date}-base.json'.format(
            file_dir=file_dir,
            fund_code=code,
            end_date=self.end_date
        )

    # 基金信息--来源爱基金
    def get_base_info(self):
        if self.base_info_is_exist():
            with open(self.file_path) as json_file:
                my_data = json.load(json_file)
                asset_str = my_data.get('asset')
                self.total_asset = float(asset_str) if asset_str else None
        else:
            url = "http://fund.10jqka.com.cn/data/client/myfund/{0}".format(
                self.fund_code)

            res = requests.get(url)  # 自动编码
            time.sleep(1)
            try:
                if res.status_code == 200:
                    res_json = res.json()
                    if res_json.get('error').get('id') == 0:
                        base_info = res.json().get('data')[0]
                        end_date = base_info.get('enddate')
                        self.total_asset = base_info.get('asset')

                        filename = '{fund_code}{end_date}-base.json'.format(
                            fund_code=self.fund_code,
                            end_date='-' + end_date if end_date else ''
                        )
                        write_json_data(base_info, filename)
                    else:
                        pprint(res_json)
                        print('code:1', self.fund_code)
                else:
                    pprint(res.raw)
                    print('code:2', self.fund_code)
                    raise('中断')
            except:
                pprint(res.raw)
                print('code:3', self.fund_code)
                raise('中断')

    def get_base_info_hz(self):
            if self.base_info_is_exist():
                with open(self.file_path) as json_file:
                    my_data = json.load(json_file)
                    asset_str = my_data.get('asset')
                    self.total_asset = float(asset_str) if asset_str else None
            else:
                url = "http://fund.10jqka.com.cn/data/client/myfund/{0}".format(
                    self.fund_code)

                res = requests.get(url)  # 自动编码
                time.sleep(1)
                try:
                    if res.status_code == 200:
                        res_json = res.json()
                        if res_json.get('error').get('id') == 0:
                            base_info = res.json().get('data')[0]
                            end_date = base_info.get('enddate')
                            self.total_asset = base_info.get('asset')

                            filename = '{fund_code}{end_date}-base.json'.format(
                                fund_code=self.fund_code,
                                end_date='-' + end_date if end_date else ''
                            )
                            write_json_data(base_info, filename)
                        else:
                            pprint(res_json)
                            print('code:1', self.fund_code)
                    else:
                        pprint(res.raw)
                        print('code:2', self.fund_code)
                        raise('中断')
                except:
                    pprint(res.raw)
                    print('code:3', self.fund_code)
                    raise('中断')

        def base_info_is_exist(self):
            return os.path.exists(self.file_path)


if __name__ == '__main__':
    fund_api = FundApier('003834')
    fund_api.get_base_info()
