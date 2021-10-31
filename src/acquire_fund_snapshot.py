'''
Desc: 爬取晨星网基金列表数据，支持保存成csv，或者存入到mysql中
File: /acquire_fund_list.py
Project: src
File Created: Saturday, 26th December 2020 11:48:55 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import math
import os
import re
import sys

sys.path.append(os.getcwd() + '/src')

from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait

from db.connect import connect
from lib.mysnowflake import IdWorker
from utils.index import get_star_count, bootstrap_thread
from utils.login import login_morning_star

connect_instance = connect()
cursor = connect_instance.cursor()

'''
判读是否当前页一致，没有的话，切换上一页，下一页操作
'''


def text_to_be_present_in_element(locator, text, next_page_locator):
    """ An expectation for checking if the given text is present in the
    specified element.
    locator, text
    """
    def _predicate(driver):
        try:
            element_text = driver.find_element_by_xpath(locator).text
            if int(element_text) != int(text):
                # 跳转指定的js执行代码
                js_content = "javascript:__doPostBack('ctl00$cphMain$AspNetPager1','{}')".format(
                    text)
                execute_return = driver.execute_script(js_content)
                print('execute_return', execute_return)
                sleep(5)

            return text == element_text
        except:
            return False

    return _predicate


def get_fund_list(page_index):
    morning_fund_selector_url = "https://www.morningstar.cn/fundselect/default.aspx"
    chrome_driver = login_morning_star(morning_fund_selector_url, False)
    # 定义起始页码
    page_count = 25 # 晨星固定分页数
    page_total = math.ceil(int(chrome_driver.find_element_by_xpath(
        '/html/body/form/div[8]/div/div[4]/div[3]/div[2]/span').text) / page_count)

    result_dir = './output/'
    output_head = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + \
        '类型' + ',' + '三年评级' + ',' + '五年评级' + ',' + '今年回报率' + '\n'
    env_snapshot_table_name = os.getenv('snapshot_table_name')
    output_file_name = env_snapshot_table_name + ".csv"
    # 设置表头
    if page_index == 1:
        with open(result_dir + output_file_name, 'w+') as csv_file:
            csv_file.write(output_head)
    while page_index <= page_total:
        # 求余
        remainder = page_total % 10
        # 判断是否最后一页
        num = (remainder +
               2) if page_index > (page_total - remainder) else 12
        xpath_str = '/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/a[%s]' % (
            num)
        print('page_index', page_index)

        # 等待，直到当前页（样式判断）等于page_num
        WebDriverWait(chrome_driver, timeout=600).until(text_to_be_present_in_element(
            "/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/span[@style='margin-right:5px;font-weight:Bold;color:red;']", str(page_index), xpath_str))
        sleep(1)
        # 列表用于存放爬取的数据
        id_list = []  # 雪花id
        code_list = []  # 基金代码
        morning_star_code_list = []  # 晨星专属代码
        name_list = []  # 基金名称
        fund_cat = []  # 基金分类
        fund_rating_3 = []  # 晨星评级（三年）
        fund_rating_5 = []  # 晨星评级（五年）
        rate_of_return = []  # 今年以来汇报（%）

        # 获取每页的源代码
        data = chrome_driver.page_source
        # 利用BeautifulSoup解析网页源代码
        bs = BeautifulSoup(data, 'lxml')
        class_list = ['gridItem', 'gridAlternateItem']  # 数据在这两个类下
        # 取出所有类的信息，并保存到对应的列表里
        for i in range(len(class_list)):
            for tr in bs.find_all('tr', {'class': class_list[i]}):
                # 雪花id
                worker = IdWorker()
                id_list.append(worker.get_id())
                tds_text = tr.find_all('td', {'class': "msDataText"})
                tds_nume = tr.find_all('td', {'class': "msDataNumeric"})
                # 基金代码
                code_a_element = tds_text[0].find_all('a')[0]
                code_list.append(code_a_element.string)
                # 从href中匹配出晨星专属代码
                current_morning_code = re.findall(
                    r'(?<=/quicktake/)(\w+)$', code_a_element.get('href')).pop(0)
                # 晨星基金专属晨星码
                morning_star_code_list.append(current_morning_code)
                name_list.append(tds_text[1].find_all('a')[0].string)
                # 基金分类
                fund_cat.append(tds_text[2].string)
                # 三年评级
                rating = get_star_count(tds_text[3].find_all('img')[0]['src'])
                fund_rating_3.append(rating)
                # 5年评级
                rating = get_star_count(tds_text[4].find_all('img')[0]['src'])
                fund_rating_5.append(rating)
                # 今年以来回报(%)
                return_value = tds_nume[3].string if tds_nume[3].string != '-' else None
                rate_of_return.append(return_value)

        print('数据准备完毕')
        fund_df = pd.DataFrame({'id': id_list, 'fund_code': code_list, 'morning_star_code': morning_star_code_list, 'fund_name': name_list, 'fund_cat': fund_cat,
                                'fund_rating_3': fund_rating_3, 'fund_rating_5': fund_rating_5, 'rate_of_return': rate_of_return})
        env_snapshot_table_name = os.getenv('snapshot_table_name')
        sql_insert = "INSERT INTO " + env_snapshot_table_name + \
            "(`id`, `fund_code`,`morning_star_code`, `fund_name`, `fund_cat`, `fund_rating_3`, `fund_rating_5`, `rate_of_return`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE fund_rating_3=VALUES(fund_rating_3), fund_rating_5=VALUES(fund_rating_5), rate_of_return=VALUES(rate_of_return);"
        # print('fund_df', fund_df)
        fund_list = fund_df.values.tolist()
        cursor.executemany(sql_insert, fund_list)
        connect_instance.commit()
        # print('fund_list', fund_list)
        # 输出为csv文件
        with open(result_dir + output_file_name, 'a') as csv_file:
            for fund_item in fund_list:
                output_line = ', '.join(str(x) for x in fund_item) + '\n'
                csv_file.write(output_line)

        # 获取下一页元素
        next_page = chrome_driver.find_element_by_xpath(
            xpath_str)
        # 点击下一页
        next_page.click()
        sleep(3)
        page_index += 1
    chrome_driver.close()
    print('end')
    # chrome_driver.close()


if __name__ == "__main__":
    page_index = 1
    fund_list = get_fund_list(page_index)
