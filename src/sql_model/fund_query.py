'''
Desc: 基金查询sql类
File: /fund_query.py
Project: sql-model
File Created: Friday, 7th May 2021 11:58:59 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from threading import Lock
from db.connect import connect

connect_instance = connect()


class FundQuery:

    def __init__(self):
        self.cursor = connect_instance.cursor()
        self.lock = Lock()

    # 需要爬取季度性信息的基金(B,C类基金除外，因为B、C基金大部分信息与A类一致)
    def get_crawler_quarter_total(self, ):
        # 过滤没有股票持仓的基金
        sql_count = "SELECT COUNT(1) FROM fund_morning_base \
        LEFT JOIN fund_morning_snapshot ON fund_morning_snapshot.fund_code = fund_morning_base.fund_code \
        WHERE fund_morning_base.fund_cat NOT LIKE '%%货币%%' \
        AND fund_morning_base.fund_cat NOT LIKE '%%纯债基金%%' \
        AND fund_morning_base.fund_cat NOT LIKE '目标日期' \
        AND fund_morning_base.fund_name NOT LIKE '%%C' \
        AND fund_morning_base.fund_name NOT LIKE '%%B' \
        AND fund_morning_base.fund_cat NOT LIKE '%%短债基金%%'"
        self.cursor.execute(sql_count)
        count = self.cursor.fetchone()
        return count[0]
