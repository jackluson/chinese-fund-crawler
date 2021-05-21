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
        self.quarter_index = '2021-Q1'
        connect_instance = connect()
        self.connect_instance = connect_instance
        self.cursor = connect_instance.cursor()
        self.lock = Lock()

    # 需要爬取季度性信息的基金(B,C类基金除外，因为B、C基金大部分信息与A类一致)
    def get_crawler_quarter_fund_total(self):
        # 过滤没有股票持仓的基金
        sql_count = "SELECT COUNT(1) FROM fund_morning_base as a \
        WHERE a.fund_cat NOT LIKE '%%货币%%' \
        AND a.fund_cat NOT LIKE '%%纯债基金%%' \
        AND a.fund_cat NOT LIKE '目标日期' \
        AND a.fund_name NOT LIKE '%%C' \
        AND a.fund_name NOT LIKE '%%B' \
        AND a.fund_cat NOT LIKE '%%短债基金%%' \
        AND a.fund_code	NOT IN( SELECT fund_code FROM fund_morning_quarter as b \
        WHERE b.quarter_index = %s);"
        self.cursor.execute(sql_count, [self.quarter_index])
        count = self.cursor.fetchone()
        return count[0]

    # 筛选基金季度性信息的基金
    def select_quarter_fund(self, page_start, page_limit):
        sql = "SELECT t.fund_code,\
            t.morning_star_code, t.fund_name, t.fund_cat \
            FROM fund_morning_base as t \
            WHERE t.fund_cat NOT LIKE '%%货币%%' \
            AND t.fund_cat NOT LIKE '%%纯债基金%%' \
            AND t.fund_cat NOT LIKE '目标日期' \
            AND t.fund_cat NOT LIKE '%%短债基金%%' \
            AND t.fund_name NOT LIKE '%%C' \
            AND t.fund_name NOT LIKE '%%B' \
            AND t.fund_code	NOT IN( SELECT fund_code FROM fund_morning_quarter as b \
            WHERE b.quarter_index = %s) LIMIT %s, %s;"
        self.lock.acquire()
        self.cursor.execute(
            sql, [self.quarter_index, page_start, page_limit])    # 执行sql语句
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

    # 更新基金资产 -- fund_morning_quarter
    def update_fund_total_asset(self, fund_code, total_asset):
        sql_update = "UPDATE fund_morning_quarter SET total_asset = %s WHERE fund_code = %s;"
        self.cursor.execute(sql_update, [total_asset, fund_code])
        self.connect_instance.commit()

    def select_top_10_stock(self, quarter_index=None, fund_code_pool=None):
        stock_sql_join = ''
        for index in range(10):
            stock_sql_join = stock_sql_join + \
                "t.top_stock_%s_code, t.top_stock_%s_name" % (
                    str(index), str(index)) + ","
        stock_sql_join = stock_sql_join[0:-1]
        fund_code_list_sql = ''
        # 判断是否传入fund_code_pool
        if isinstance(fund_code_pool, list):
            if len(fund_code_pool) == 0:
                return ()
            list_str = ', '.join(fund_code_pool)
            fund_code_list_sql = "AND t.fund_code IN (" + list_str + ")"
        sql_query_quarter = "SELECT t.fund_code," + stock_sql_join + \
            " FROM fund_morning_stock_info as t WHERE t.quarter_index = %s AND t.stock_position_total > 20 " + \
            fund_code_list_sql + \
            ";"  # 大于20%股票持仓基金
        if quarter_index == None:
            quarter_index = self.quarter_index
        self.cursor.execute(sql_query_quarter, [quarter_index])    # 执行sql语句
        results = self.cursor.fetchall()    # 获取查询的所有记录
        return results

    # 分组查询特定股票的每个季度基金持有总数
    def select_special_stock_fund_count(self, stock_name, fund_code_pool=None):
        stock_sql_join = '('
        for index in range(10):
            stock_sql_join = stock_sql_join + \
                "t.top_stock_%s_name = '%s' or " % (
                    str(index), stock_name)
        stock_sql_join = stock_sql_join[0:-3] + ')'
        fund_code_list_sql = ''
        # 判断是否传入fund_code_pool
        if isinstance(fund_code_pool, list):
            if len(fund_code_pool) == 0:
                return ()
            list_str = ', '.join(fund_code_pool)
            fund_code_list_sql = "t.fund_code IN (" + list_str + ") AND "
        sql_query_sqecial_stock_fund_count = "SELECT count(1) as count, quarter_index FROM fund_morning_stock_info as t WHERE t.stock_position_total > 20 AND " + \
            fund_code_list_sql + \
            stock_sql_join + " GROUP BY t.quarter_index;"  # 大于20%股票持仓基金

        self.cursor.execute(sql_query_sqecial_stock_fund_count)    # 执行sql语句
        results = self.cursor.fetchall()    # 获取查询的所有记录
        return results
