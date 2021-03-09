'''
Desc: 爬取基金详情页信息
File: /fund_info_crawler.py
Project: src
File Created: Monday, 8th March 2021 5:43:27 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import re
from time import sleep
from bs4 import BeautifulSoup
from utils import parse_cookiestr, set_cookies, login_site


class FundInfo:
    # 初始化定义，利用基金代码、基金名称进行唯一化
    def __init__(self, code, namecode, name,  chrome_driver, morning_cookies):
        self.season_number = '2021-1'
        self.fund_code = code  # 基金代码，需要初始化赋值
        self.fund_name = name  # 基金名称，需要初始化赋值
        self.morning_star_code = namecode  # 基金编码，晨星网特有，需要建立索引表

        self.morning_cookies = morning_cookies or None
        self.chrome_driver = chrome_driver or None

        # 通过晨星网获取
        self.fund_cat = None  # 基金分类
        self.found_date = None  # 成立时间
        self.total_asset = None  # 总资产
        self.investname_style = None  # 投资风格
        self.manager = dict()  # 基金经理,name,id,管理时间
        self.company = None  # 基金公司
        self.three_month_retracement = 0.0  # 三个月最大回撤
        self.bond_total_position = dict()  # 债券总仓位、前五大持仓
        self.stock_total_position = dict()  # 股票总仓位、前十大持仓
        self.ten_top_stock_list = []  # 股票十大持仓股信息
        self.risk_assessment = dict()  # 标准差 风险系数 夏普比
        self.risk_statistics = dict()  # 阿尔法 贝塔 R平方值
    # 处理基金详情页跳转

    def login_morning_star(self, cookie_str=None):
        login_url = 'https://www.morningstar.cn/membership/signin.aspx'
        if self.chrome_driver == None:
            from selenium import webdriver
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--no-sandbox")
            # chrome_driver = webdriver.Chrome("/usr/local/chromedriver")
            self.chrome_driver = webdriver.Chrome(options=chrome_options)
            self.chrome_driver.set_page_load_timeout(12000)
            """
        模拟登录,支持两种方式：
            1. 设置已经登录的cookie
            2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
        """
        if cookie_str:
            set_cookies(self.chrome_driver,
                        login_url, cookie_str)
        else:
            if self.morning_cookies == None:
                login_status = login_site(
                    self.chrome_driver, login_url)
                if login_status:
                    print('login success')
                    sleep(3)
                else:
                    print('login fail')
                    exit()
                # 获取网站cookie
                morning_cookies = self.chrome_driver.get_cookies()
            else:
                self.morning_cookies = self.chrome_driver.get_cookies()
                # print('cookies', self.morning_cookies)  # 打印设置成功的cookie
    # 更新基金信息，从晨星网上抓取，利用selinum原理

    def go_fund_url(self, cookie_str=None):
        self.login_morning_star(cookie_str)
        morning_fund_selector_url = "https://www.morningstar.cn/quicktake/" + \
            self.morning_star_code

        # 获取基金三个月内的最大回撤
        self.chrome_driver.get(morning_fund_selector_url)  # 打开爬取页面
        sleep(6)
        # 判断是否页面出错，重定向，如果是的话跳过
        if self.chrome_driver.current_url == 'https://www.morningstar.cn/errors/defaulterror.html':
            return False

    def get_fund_base_info(self,  cookie_str=None):
        # 基金分类
        self.fund_cat = self.chrome_driver.find_element_by_id(
            'qt_base').find_element_by_class_name("category").text
        # 成立时间
        self.found_date = self.chrome_driver.find_element_by_id(
            'qt_base').find_element_by_class_name("inception").text
        # 基金公司
        self.company = self.chrome_driver.find_element_by_id(
            'qt_management').find_element_by_xpath("//ul[@id='qt_management']/li[4]/span[@class='col2 comp']/a").text
