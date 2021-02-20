'''
Desc: 爬取晨星网基金列表数据，支持保存成csv，或者存入到mysql中
File: /acquire_fund_list.py
Project: src
File Created: Saturday, 26th December 2020 11:48:55 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import re
import math
import os
# import pymysql
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from lib.mysnowflake import IdWorker
from utils import parse_cookiestr, set_cookies, login_site, get_star_count

# connect = pymysql.connect(host='127.0.0.1', user='root',
#                           password='rootroot', db='fund_work', charset='utf8')
# cursor = connect.cursor()

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
            # 比给定的页码小的话，触发下一页
            if int(element_text) < int(text):
                print(element_text, text)
                next_page = driver.find_element_by_xpath(
                    next_page_locator)
                # driver.refresh()
                next_page.click()
                sleep(5)
                # 比给定的页码大的话，触发上一页
            elif int(element_text) > int(text):
                print(element_text, text)
                prev_page = driver.find_element_by_xpath(
                    '/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/a[2]')
                # driver.refresh()
                prev_page.click()
                sleep(5)
            return text == element_text
        except:
            return False

    return _predicate


def get_fund_list(cookie_str=None):
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(12000)    # 防止页面加载个没完

    morning_fund_selector_url = "https://www.morningstar.cn/fundselect/default.aspx"
    # "https://cn.morningstar.com/quickrank/default.aspx"
    """
    模拟登录,支持两种方式：
        1. 设置已经登录的cookie
        2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
    """
    if cookie_str:
        set_cookies(chrome_driver, morning_fund_selector_url, cookie_str)
    else:
        morning_cookies = ""
        if morning_cookies == "":
            login_status = login_site(chrome_driver, morning_fund_selector_url)
            if login_status:
                print('login success')
                sleep(3)
            else:
                print('login fail')
                exit()
            # 获取网站cookie
            morning_cookies = chrome_driver.get_cookies()
        else:
            chrome_driver.get(morning_fund_selector_url)  # 再次打开爬取页面
            print(chrome_driver.get_cookies())  # 打印设置成功的cookie
    # 定义起始页码
    page_num = 1
    page_count = 25
    page_num_total = math.ceil(int(chrome_driver.find_element_by_xpath(
        '/html/body/form/div[8]/div/div[4]/div[3]/div[2]/span').text) / page_count)
    # 爬取共306页
    result_dir = './output/'
    output_head = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + \
        '类型' + ',' + '三年评级' + ',' + '五年评级' + ',' + '今年回报率' + '\n'
    # 设置表头
    if page_num == 1:
        with open(result_dir + 'fund_morning_star.csv', 'w+') as csv_file:
            csv_file.write(output_head)
    while page_num <= page_num_total:
        # 求余
        remainder = page_num_total % 10
        # 判断是否最后一页
        num = (remainder +
               2) if page_num > (page_num_total - remainder) else 12
        xpath_str = '/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/a[%s]' % (
            num)
        print('page_num', page_num)
        # 等待，直到当前页（样式判断）等于page_num
        WebDriverWait(chrome_driver, timeout=600).until(text_to_be_present_in_element(
            "/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/span[@style='margin-right:5px;font-weight:Bold;color:red;']", str(page_num), xpath_str))
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
        class_list = ['gridItem', 'gridAlternateItem']  # 数据在这两个类下面

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
        fund_df = pd.DataFrame({'fund_code': code_list, 'morning_star_code': morning_star_code_list, 'fund_name': name_list, 'fund_cat': fund_cat,
                                'fund_rating_3': fund_rating_3, 'fund_rating_5': fund_rating_5, 'rate_of_return': rate_of_return})
        sql_insert = "replace into fund_morning_star(`id`, `fund_code`,`morning_star_code`, `fund_name`, `fund_cat`, `fund_rating_3`, `fund_rating_5`, `rate_of_return`) values(%s, %s, %s, %s, %s, %s, %s, %s)"
        fund_list = fund_df.values.tolist()
        # cursor.executemany(sql_insert, fund_list)
        # connect.commit()
        # sql_insert = "insert into fund_morning_star(`fund_code`, `fund_name`, `fund_cat`, `fund_rate_3`, `fund_rate_5`, `rate_of_return`) values(%s, %s, %s, %s, %s, %s)"
        # ALTER TABLE fund_morning_star  MODIFY COLUMN update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        print('fund_list', fund_list)
        with open(result_dir + 'fund_morning_star.csv', 'a') as csv_file:
            for fund_item in fund_list:
                output_line = ', '.join(str(x) for x in fund_item) + '\n'
                csv_file.write(output_line)

        # 获取下一页元素
        next_page = chrome_driver.find_element_by_xpath(
            xpath_str)
        # 点击下一页
        next_page.click()
        page_num += 1
    chrome_driver.close()
    print('end')
    # chrome_driver.close()


if __name__ == "__main__":
    cookie_str = 'Hm_lvt_eca85e284f8b74d1200a42c9faa85464=1610788772; user=username=18219112108@163.com&nickname=camel-lu&status=Free&password=KFPJOQuxD1w=; MS_LocalEmailAddr=18219112108@163.com=; ASP.NET_SessionId=0aenwime2ljio155dogxybev; Hm_lvt_eca85e284f8b74d1200a42c9faa85464=; MSCC=GUflpfSQOVM=; authWeb=5220F774042557D9FA31A08FA717CB8DE74F5016A9ADDB25C269FBB69C7DF340D59E6E63061444FE0B93DBB4F5AAFA6B1D21155C3FAA68C79992F39B9986630AEB6F674F242B6B792693ABB6162784CA329333200C2BBDD44021A1F38E80A363F157CD24D4D0E527C3E8F23E3DEA13C5D9950FF5; Hm_lpvt_eca85e284f8b74d1200a42c9faa85464=1613479786'

    fund_list = get_fund_list()
