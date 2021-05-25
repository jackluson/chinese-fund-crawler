'''
Desc: 基金查询sql类
File: /fund_query.py
Project: sql-model
File Created: Friday, 7th May 2021 11:58:59 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import time
from threading import Lock
from db.connect import connect


def format_sql(table_name, field_dict, prefix="AND"):
    print("field_dict", field_dict['name'])
    sql_str = ''
    field_name = field_dict.get('name')
    field_value = field_dict.get('value')
    operator = field_dict.get('operator')
    if not field_name or not field_value or not operator:
        return sql_str
    format_dict = {
        "prefix": prefix,
        'table_name': table_name,
        'field_name': field_name,
        "operator": operator,
        "value": field_value
    }
    sql_str = '{prefix} {table_name}.{field_name} {operator} {value}'.format(
        **format_dict)
    return sql_str


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

    def select_high_score_funds(self, *, quarter_index=None):
        """获取高分基金池

        Args:
            quarter_index (string, optional): 查询季度. Defaults to None.

        Returns:
            []tuple: 高分基金池
        """
        last_year_time = time.localtime(time.time() - 365 * 24 * 3600)
        last_year_date = time.strftime('%Y-%m-%d', last_year_time)

        if quarter_index == None:
            quarter_index = self.quarter_index
        sql = "SELECT a.fund_code, b.fund_name, a.quarter_index, a.total_asset , a.manager_start_date, \
                    a.investname_style, a.three_month_retracement, a.june_month_retracement, a.risk_assessment_sharpby,\
                    a.risk_statistics_alpha, a.risk_statistics_beta, a.risk_statistics_r_square, a.risk_assessment_standard_deviation,\
                    a.risk_assessment_risk_coefficient, a.risk_rating_2, a.risk_rating_3, a.risk_rating_5, a.morning_star_rating_5,\
                    a.morning_star_rating_3, a.stock_position_total, a.stock_position_ten FROM fund_morning_quarter as a \
                    LEFT JOIN fund_morning_base AS b ON a.fund_code = b.fund_code \
                    WHERE b.fund_name NOT LIKE '%%C' AND b.fund_name NOT LIKE '%%E'  AND a.quarter_index = %s AND \
                    a.morning_star_rating_5 >= 3 AND a.morning_star_rating_3 = 5 AND a.stock_position_total >= 50 AND a.stock_position_ten <= 60 \
                    AND a.risk_assessment_sharpby >1 AND a.risk_rating_2 > 1 AND a.risk_rating_3 > 1 AND a.risk_rating_5 > 1 AND a.manager_start_date < %s ORDER BY a.risk_assessment_sharpby DESC , a.three_month_retracement DESC "
        self.lock.acquire()
        self.cursor.execute(sql, [quarter_index, last_year_date])    # 执行sql语句
        results = self.cursor.fetchall()    # 获取查询的所有记录
        self.lock.release()
        return results

    def select_certain_condition_funds(self, *, quarter_index=None, morning_star_rating_5=None, morning_star_rating_3=None, manager_start_date=None):
        if quarter_index == None:
            quarter_index = self.quarter_index
        last_year_time = time.localtime(time.time() - 365 * 24 * 3600)
        last_year_date = time.strftime('%Y-%m-%d', last_year_time)
        morning_star_rating_3_sql = format_sql('a', {
            'name': 'morning_star_rating_3',
            **morning_star_rating_3
        })
        # site = {"name": "菜鸟教程", "url": ""}
        # print("网站名：{name}, 地址 {url}".format(**site))
        # if morning_star_rating_5 not None:

        sql = "SELECT a.fund_code FROM fund_morning_quarter as a \
            LEFT JOIN fund_morning_base AS b ON a.fund_code = b.fund_code \
            WHERE a.quarter_index = '{quarter_index}' AND b.fund_name NOT LIKE '%%C' AND b.fund_name NOT LIKE '%%E' {morning_star_rating_5} {morning_star_rating_3} AND a.stock_position_total >= 50 AND a.stock_position_ten <= 60 \
            AND a.risk_assessment_sharpby >1 AND a.risk_rating_2 > 1 AND a.risk_rating_3 > 1 AND a.risk_rating_5 > 1 AND a.manager_start_date < '{manager_start_date}'"

        format_dict = {
            'quarter_index': quarter_index,
            'morning_star_rating_5': "AND a.morning_star_rating_5 >= 3",
            'morning_star_rating_3': morning_star_rating_3_sql,
            'manager_start_date': str(last_year_date)
        }
        sql_format = sql.format(**format_dict)
        self.lock.acquire()
        self.cursor.execute(sql_format)    # 执行sql语句
        results = self.cursor.fetchall()    # 获取查询的所有记录
        self.lock.release()
        fund_pool = []
        for item in results:
            fund_code = item[0]
            fund_pool.append(fund_code)
        return fund_pool

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
            escape_name = stock_name.replace("'", "\\'")
            stock_sql_join = stock_sql_join + \
                "t.top_stock_{0}_name = '{1}' or ".format(
                    str(index), escape_name)
        stock_sql_join = stock_sql_join[0:-3] + ')'
        fund_code_list_sql = ''
        # 判断是否传入fund_code_pool
        if isinstance(fund_code_pool, list):
            if len(fund_code_pool) == 0:
                return ()
            list_str = ', '.join(fund_code_pool)
            fund_code_list_sql = "t.fund_code IN (" + list_str + ") AND "
        sql_query_sqecial_stock_fund_count = "SELECT count(1) as count, quarter_index FROM fund_morning_stock_info as t WHERE t.stock_position_total > 20 AND " + \
            fund_code_list_sql + stock_sql_join + \
            " GROUP BY t.quarter_index;"  # 大于20%股票持仓基金

        self.cursor.execute(sql_query_sqecial_stock_fund_count)    # 执行sql语句
        # print(self.cursor._last_executed)
        results = self.cursor.fetchall()    # 获取查询的所有记录
        return results
