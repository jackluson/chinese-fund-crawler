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


class FundQuery:

    def __init__(self):
        connect_instance = connect()
        self.connect_instance = connect_instance
        self.cursor = connect_instance.cursor()
        self.lock = Lock()

    # 需要爬取季度性信息的基金(B,C类基金除外，因为B、C基金大部分信息与A类一致)
    def get_crawler_quarter_fund_total(self):
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

    # 筛选基金季度性信息的基金
    def select_quarter_fund(self, page_start, page_limit):
        sql = "SELECT t.fund_code,\
            t.morning_star_code, t.fund_name, t.fund_cat \
            FROM fund_morning_base as t \
            LEFT JOIN fund_morning_snapshot as f ON f.fund_code = t.fund_code \
            WHERE t.fund_cat NOT LIKE '%%货币%%' \
            AND t.fund_cat NOT LIKE '%%纯债基金%%' \
            AND t.fund_cat NOT LIKE '目标日期' \
            AND t.fund_cat NOT LIKE '%%短债基金%%' \
            AND t.fund_name NOT LIKE '%%C' \
            AND t.fund_name NOT LIKE '%%B' \
            ORDER BY f.fund_rating_5 DESC,f.fund_rating_3 DESC, \
            t.fund_cat, t.fund_code LIMIT %s, %s"
        self.lock.acquire()
        self.cursor.execute(
            sql, [page_start, page_limit])    # 执行sql语句
        results = self.cursor.fetchall()    # 获取查询的所有记录
        self.lock.release()
        return results

    # 筛选同类基金，除了A类
    def select_similar_fund(self, similar_name):
        sql_similar = "SELECT t.fund_code,\
                t.morning_star_code, t.fund_name \
                FROM fund_morning_base as t \
                LEFT JOIN fund_morning_snapshot as f ON f.fund_code = t.fund_code \
                WHERE t.fund_name LIKE %s \
                AND t.fund_name NOT LIKE '%%A';"
        self.lock.acquire()
        self.cursor.execute(sql_similar, [similar_name + '%'])
        results = self.cursor.fetchall()    # 获取查询的所有记录
        self.lock.release()
        return results

    # A类基金
    def select_all_a_class_fund(self, start, limit):
        sql_query_a_class = "SELECT fund_code, SUBSTRING(fund_name, 1, CHAR_LENGTH(fund_name)-1) as name, fund_name FROM fund_morning_base WHERE fund_name LIKE '%%A' LIMIT %s, %s ;"
        self.cursor.execute(sql_query_a_class, [start, limit])    # 执行sql语句
        all_a_results = self.cursor.fetchall()
        return all_a_results

    # 同名C类基金
    def select_c_class_fund(self, name):
        sql_query_c_class = "SELECT fund_code, fund_name FROM fund_morning_base WHERE fund_name LIKE '" + \
            name + "C';"
        self.cursor.execute(sql_query_c_class)
        c_class_result = self.cursor.fetchone()
        return c_class_result

    # 更新基金资产
    def update_fund_total_asset(self, fund_code, total_asset):
        sql_update = "UPDATE fund_morning_quarter SET total_asset = %s WHERE fund_code = %s;"
        self.cursor.execute(sql_update, [total_asset, fund_code])
        self.connect_instance.commit()
