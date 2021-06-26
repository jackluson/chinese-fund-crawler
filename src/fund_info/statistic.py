'''
Desc: 基金统计
File: /statistic.py
Project: fund_info
File Created: Thursday, 13th May 2021 11:04:55 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import time
import datetime
import os
import sys
from pprint import pprint
sys.path.append('../')
sys.path.append(os.getcwd() + '/src')
from utils.index import get_quarter_index, fisrt_match_condition_from_list
from sql_model.fund_query import FundQuery


class FundStatistic:
    def __init__(self):
      # 统计上一个季度
        last_quarter_time = time.localtime(time.time() - 3 * 30 * 24 * 3600)
        # time.strftime("%m-%d", last_quarter_time)
        year = time.strftime("%Y", last_quarter_time)
        date = time.strftime("%m-%d", last_quarter_time)
        index = get_quarter_index(date)
        quarter_index = year + '-Q' + str(index)
        self.quarter_index = quarter_index
        self.each_query = FundQuery()

    def all_stock_fund_count(self, *, quarter_index=None, fund_code_pool=None, filter_count=100):
        """查询某一个季度基金的十大持仓，并对持仓股票进行汇总统计，并根据filter_count进行过滤

        Args:
            quarter_index (string, optional): [description]. Defaults to None.取self.quarter_index
            fund_code_pool (string[], optional): [description]. Defaults to None. 传入查询的基金池，为None默认查询全部
            filter_count (int, optional): [description]. Defaults to 100. 过滤门槛，过滤掉一些持仓低的股票

        Returns:
            tuple[]: 每只股票的名称，以及对应持仓基金个数的list
        """

        quarter_index = quarter_index if quarter_index else self.quarter_index
        results = self.each_query.select_top_10_stock(
            quarter_index,
            fund_code_pool
        )
        code_dict = dict()
        for result in results:
            # print(result)
            totol_asset =  result[2]
            for index in range(4, len(result), 3):
                code = result[index]
                name = result[index + 1]  # 仅以股票名称为key，兼容港股，A股
                portion = result[index + 2]
                if code == None or name == None:
                    #print('index', index, 'code', code, 'name', name)
                    #print('基金名称', result[1],'基金代码', result[0])
                    continue
                key = fisrt_match_condition_from_list(list(code_dict), code)
                holder_asset = round(portion * totol_asset / 100, 4) if totol_asset and portion else 0
                if key == None and code and name:
                    key = str(code) + '-' + str(name)
                if(key in code_dict and code != None):
                    count = code_dict[key]['count'] + 1
                    holder_asset = code_dict[key]['holder_asset'] + holder_asset
                    code_dict[key] = {
                        'count': count,
                        'holder_asset': holder_asset
                    }
                else:
                    code_dict[key] = {
                        'count': 1,
                        'holder_asset': holder_asset
                    }
        filer_dict = dict()
 
        for key, value in code_dict.items():  # for (key,value) in girl_dict.items() 这样加上括号也可以
            if value['count'] > filter_count and key != None:
                filer_dict[key] = value
                # print(key + ":" + str(value))
        return sorted(filer_dict.items(), key=lambda x: x[1]['count'], reverse=True)

    def all_stock_fund_count_and_details(self, *, quarter_index=None, fund_code_pool=None, filter_count=100):
        """查询某一个季度基金的十大持仓，并对持仓股票进行汇总统计，并根据filter_count进行过滤

        Args:
            quarter_index (string, optional): [description]. Defaults to None.取self.quarter_index
            fund_code_pool (string[], optional): [description]. Defaults to None. 传入查询的基金池，为None默认查询全部
            filter_count (int, optional): [description]. Defaults to 100. 过滤门槛，过滤掉一些持仓低的股票

        Returns:
            tuple[]: 每只股票的名称，以及对应持仓基金个数的list
        """

        quarter_index = quarter_index if quarter_index else self.quarter_index
        results = self.each_query.select_top_10_stock(
            quarter_index,
            fund_code_pool
        )
        code_dict = dict()
        for result in results:
            #print(result)
            fund_info = {
                '基金代码': result[0],
                '基金名称': result[1],
                '基金金额': result[2],
                '股票总仓位': result[3],
            }
            totol_asset =  result[2]
            for index in range(4, len(result), 3):
                code = result[index]
                name = result[index + 1]
                portion = result[index + 2]
                if code == None or name == None:
                    continue
                key = fisrt_match_condition_from_list(list(code_dict), code)
                if key == None and code and name:
                    key = str(code) + '-' + str(name)
                #key = str(name)
                holder_asset = round(portion * totol_asset / 100, 4) if totol_asset and portion else 0
                if(key in code_dict and code != None):
                    code_dict[key]['count'] = code_dict[key]['count'] + 1
                    code_dict[key]['fund_list'].append({
                        **fund_info,
                        '仓位占比': portion,
                        '持有市值(亿元)': holder_asset,
                        '仓位排名': int(index / 3)
                    })
                else:
                    code_dict[key] = {
                        'count': 1,
                        'fund_list': [{
                        **fund_info,
                        '仓位占比': portion,
                        '持有市值(亿元)': holder_asset,
                        '仓位排名': int(index / 3)
                    }]
                    }
        #for key, value in code_dict.items(): 
        #    print('key, value', key, value)
        return sorted(code_dict.items(), key=lambda x: x[1]['count'], reverse=True)
    # 分组查询特定股票的每个季度基金持有总数
    def item_stock_fund_count(self, stock_code, fund_code_pool=None):
        return self.each_query.select_special_stock_fund_count(stock_code, fund_code_pool)

    def select_special_stock_special_quarter_info(self, stock_code, quarter_index=None,fund_code_pool=None):
        result =  self.each_query.select_special_stock_special_quarter_info(stock_code, quarter_index, fund_code_pool)
        target_stock_dict = {
            'count': len(result)
        }
        total_holder_asset = 0
        for holders in result:
            total_asset = holders[1]
            for index in range(2, len(holders), 2):
                code = holders[index]
                if code == stock_code:
                    portion = holders[index+1]
                    holder_asset = round(portion * total_asset / 100, 4) if total_asset and portion else 0
                    total_holder_asset = total_holder_asset + holder_asset
                    break
        target_stock_dict['holder_asset'] = total_holder_asset
        return target_stock_dict


    def select_fund_pool(self, *, morning_star_rating_5="", morning_star_rating_3="", **args):
        return self.each_query.select_certain_condition_funds(
            morning_star_rating_5=morning_star_rating_5,
            morning_star_rating_3=morning_star_rating_3,
            **args
        )
