'''
Desc:
File: /sync_fund_base.py
File Created: Sunday, 30th October 2022 2:53:56 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import math
import re
from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from crud.query import query_all_fund, query_empty_company_and_found_date_fund
from models.fund import FundBase
from fund_info.crawler import FundSpider
from utils.index import bootstrap_thread
from utils.driver import create_chrome_driver, text_to_be_present_in_element
from utils.login import login_morning_star


def sync_fund_base(page_index):
    morning_fund_selector_url = "https://www.morningstar.cn/fundselect/default.aspx"
    chrome_driver = create_chrome_driver()
    login_morning_star(chrome_driver, morning_fund_selector_url)
    page_count = 25 # 晨星固定分页数
    page_total = math.ceil(int(chrome_driver.find_element(By.XPATH,
        '/html/body/form/div[8]/div/div[4]/div[3]/div[2]/span').text) / page_count)
    all_fund_dict = query_all_fund()
    all_fund_codes = all_fund_dict.keys()
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
         # 获取每页的源代码
        data = chrome_driver.page_source
        # 利用BeautifulSoup解析网页源代码
        bs = BeautifulSoup(data, 'lxml')
        class_list = ['gridItem', 'gridAlternateItem']  # 数据在这两个类下
        # 取出所有类的信息，并保存到对应的列表里
        for i in range(len(class_list)):
            tr_list = bs.find_all('tr', {'class': class_list[i]})
            for tr_index in range(len(tr_list)):
                # 雪花id
                tr = tr_list[tr_index]
                tds_text = tr.find_all('td', {'class': "msDataText"})
                # 基金代码
                code_a_element = tds_text[0].find_all('a')[0]
                cur_fund_code = code_a_element.string
                cur_morning_star_code = re.findall(
                    r'(?<=/quicktake/)(\w+)$', code_a_element.get('href')).pop(0)
                cur_fund_name = tds_text[1].find_all('a')[0].string
                cur_fund_cat = tds_text[2].string
                if cur_fund_code in all_fund_codes:
                    exit_fund = all_fund_dict.get(cur_fund_code)
                    if (cur_morning_star_code != exit_fund['morning_star_code']) or (cur_fund_name != exit_fund['fund_name']) or (cur_fund_cat != exit_fund['fund_cat']) :
                        fund_base_params = {
                            **exit_fund,
                            'morning_star_code': cur_morning_star_code,
                            'fund_name': cur_fund_name,
                            'fund_cat': cur_fund_cat
                        }
                        fund_base = FundBase(**fund_base_params)
                        fund_base.upsert()
                elif cur_fund_code:
                    fund_base_params = {
                        'fund_code': cur_fund_code,
                        'morning_star_code': cur_morning_star_code,
                        'fund_name': cur_fund_name,
                        'fund_cat': cur_fund_cat
                    }
                    fund_base = FundBase(**fund_base_params)
                    print('fund_name:', cur_fund_name, 'fund_code:', cur_fund_code, 'morning_star_code:', cur_morning_star_code)
                    fund_base.upsert()
        # 获取下一页元素
        next_page = chrome_driver.find_element(By.XPATH, xpath_str)
        # 点击下一页
        next_page.click()
        sleep(3)
        page_index += 1
    chrome_driver.close()
    print('end')

def further_complete_base_info():
    all_funds = query_empty_company_and_found_date_fund(0, 10000)
    error_funds = []
    def crawlData(start, end):
        login_url = 'https://www.morningstar.cn/membership/signin.aspx'
        chrome_driver = create_chrome_driver()
        login_morning_star(chrome_driver, login_url)
        page_start = start
        page_limit = 10
        # 遍历从基金列表的单支基金
        while(page_start < end):
            page_end = page_start + page_limit
            results = all_funds[page_start:page_end]
            # results = query_empty_company_and_found_date_fund(page_start, page_limit)
            for record in results:
                fund_code = record.fund_code
                morning_star_code = record.morning_star_code
                fund_name = record.fund_name
                each_fund = FundSpider(fund_code, morning_star_code, fund_name, chrome_driver)
                # 是否能正常跳转到基金详情页
                is_error_page = each_fund.go_fund_url()
                if is_error_page == True:
                    error_funds.append(each_fund.fund_code)
                    continue
                each_fund.get_fund_base_info()
                # 去掉没有成立时间的
                if each_fund.found_date == '-' or each_fund.found_date == None:
                    # lock.acquire()
                    error_funds.append(each_fund.fund_code)
                    # lock.release()
                    continue
                # 拼接sql需要的数据
                base_dict = {
                    'fund_code': fund_code,
                    'morning_star_code': morning_star_code,
                    'fund_name': each_fund.fund_name,
                    'fund_cat': each_fund.fund_cat ,
                    'company': each_fund.company,
                    'found_date': each_fund.found_date
                }
                fund_base = FundBase(**base_dict)
                fund_base.upsert()
            page_start = page_start + page_limit
            print('page_start', page_start)
        chrome_driver.close()
    bootstrap_thread(crawlData, len(all_funds), 3)
if __name__ == '__main__':
    #127, 300, 600-
    page_index = 1
    # sync_fund_base(page_index)
    further_complete_base_info()
    