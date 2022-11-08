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
import sys
from pprint import pprint
sys.path.append('../')
sys.path.append(os.getcwd() + '/src')
from utils.file_op import write_fund_json_data
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

class FundApier:
    def __init__(self, code, *, end_date=None, platform='ai_fund'):
        self.fund_code = code
        self.cur_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        self.end_date = end_date
        self.platform = platform
        self.total_asset = None
        self.buy_status = None
        self.sell_status = None
        # 默认的爱基金
        self.file_dir = os.getcwd() + '/output/json/' + self.platform + \
            '/' + self.cur_date + '/'
        self.file_path = '{file_dir}{fund_code}-{end_date}-base.json'.format(
            file_dir=self.file_dir,
            fund_code=code,
            end_date=self.end_date
        )
    def get_client_headers(self, *, referer="https://danjuanfunds.com"):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
            'Origin': referer,
            'Referer': referer,
        }
        return headers
    def get_total_asset(self):
        if self.base_info_is_exist():
            return self.get_asset_from_json()
        if self.platform == 'ai_fund':
            return self.get_base_info_ai()
        elif self.platform == 'zh_fund':
            return self.get_base_info_zh()
        elif self.platform == 'danjuan':
            return self.get_base_info_from_danjuan()

    def get_asset_from_json(self):
        with open(self.file_path) as json_file:
            my_data = json.load(json_file)
            asset_str = my_data.get(
                'asset') if self.platform == 'ai_fund' else my_data.get('FundScope')[0:-1]
            try:
                self.total_asset = float(asset_str)
                return self.total_asset
            except ValueError:
                print(asset_str, "not a number")

    # 基金信息--来源爱基金
    def get_base_info_ai(self):
        url = "http://fund.10jqka.com.cn/data/client/myfund/{0}".format(
            self.fund_code)
        headers = self.get_client_headers(referer="https://fund.10jqka.com.cn")
        res = session.get(url, headers=headers)  # 自动编码
        time.sleep(2)
        try:
            if res.status_code == 200:
                res_json = res.json()
                if res_json.get('error').get('id') == 0:
                    base_info = res.json().get('data')[0]
                    end_date = base_info.get('enddate')
                    total_asset = base_info.get('asset')
                    self.write_info_in_json(end_date, base_info)
                    try:
                        self.total_asset = float(total_asset)
                        return self.total_asset
                    except ValueError:
                        print("ai->", self.fund_code, total_asset, "not a number")
                        
                else:
                    pprint(res_json)
                    print('code:1', self.fund_code)
            else:
                print('url:', url)
                print('code:2', self.fund_code)
                raise('中断')
        except:
            print('url:', url)
            print('code:3', self.fund_code)
            raise('中断')

    # 基金信息--来源展恒基金
    def get_base_info_zh(self):
        url = "https://www.myfund.com/webinterface/Bamboo.ashx?command={0}".format(
            'fundInfoHead_NEW')
        headers = self.get_client_headers(referer="https://www.myfund.com")
        payload = {
            'fundcode': self.fund_code,
        }
        res = session.post(url, headers=headers, data=payload)
        res.encoding = "utf-8"
        time.sleep(1)
        try:
            if res.status_code == 200:
                res_json = res.json()
                fund_scope = res_json.get('FundScope')
                if res_json.get('Msg') == 'OK' and fund_scope != None:
                    end_date = res_json.get('DealDate')
                    total_asset = fund_scope[0:-1]
                    self.write_info_in_json(end_date, res_json)
                    try:
                        self.total_asset = float(total_asset)
                        return self.total_asset
                    except ValueError:
                        print("zh->", self.fund_code, total_asset, "not a number")
                else:
                    pprint(res_json)
                    print('code:1', self.fund_code)
            else:
                pprint(res.content)
                print('code:2', self.fund_code)
                raise('中断')
        except:
            print('code:3', self.fund_code)
            raise('中断')

    def get_analyse_info_zh(self):
            url = "https://www.myfund.com/webinterface/Bamboo.ashx?command={0}".format(
                'singlefundAnalyse')
            headers = self.get_client_headers(referer="https://www.myfund.com")
            payload = {
                'fundcode': self.fund_code,
            }
            # res = requests.post(url, headers=headers, data=payload, verify=False)
            res = requests.post(url, headers=headers, data=payload)
            # print("res", res)
            res.encoding = "utf-8"
            time.sleep(1)
            try:
                if res.status_code == 200:
                    res_json = res.json()
                    buy_status = res_json.get('BuyStatus')
                    sell_status = res_json.get('SellStatus')
                    if res_json.get('Msg') == 'OK' and buy_status != None:
                        self.sell_status = sell_status
                        self.buy_status = buy_status
                    else:
                        pprint(res_json)
                        print('code:1', self.fund_code)
                else:
                    pprint(res.content)
                    print('code:2', self.fund_code)
                    raise('中断')
            except:
                print('code:3', self.fund_code)
                raise('中断')

    def get_base_info_from_danjuan(self):
        url = "https://danjuanfunds.com/djapi/fund/{0}".format(self.fund_code)
        headers = self.get_client_headers()
        res = session.get(url, headers=headers)
        try:
            if res.status_code == 200:
                res_json = res.json()
                if res_json.get('result_code') == 0:
                    base_info = res.json().get('data')
                    total_asset = base_info.get('totshare')
                    if(total_asset.endswith('万')):
                        total_asset = round(float(total_asset[0:-1]) / 10000, 3)
                    elif(total_asset.endswith('亿')):
                        total_asset = float(total_asset[0:-1])
                    else:
                        print("danjuan->", self.fund_code, total_asset, "not a number")
                        return
                    self.total_asset = total_asset
                    return self.total_asset
            else:
                pprint(res.content)
                print('code:2', self.fund_code)
                raise('中断')
        except:
            print('code:3', self.fund_code)
            raise('中断')
    def write_info_in_json(self, end_date, json_data):
        filename = '{fund_code}{end_date}-base.json'.format(
            fund_code=self.fund_code,
            end_date='-' + end_date if end_date else ''
        )
        write_fund_json_data(json_data, filename, self.file_dir)

    def base_info_is_exist(self):
        return os.path.exists(self.file_path)


if __name__ == '__main__':
    fund_api = FundApier('011140', end_date='2021-05-31',)
    fund_api.get_base_info_from_danjuan()
    # print("fund_api", fund_api)
