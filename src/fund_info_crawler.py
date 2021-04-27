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
from utils import parse_cookiestr, set_cookies, login_site, get_star_count
from selenium.common.exceptions import NoSuchElementException


class FundSpider:
    # 初始化定义，利用基金代码、基金名称进行唯一化
    def __init__(self, code, namecode, name,  chrome_driver, morning_cookies):
        self.quarter_index = '2021-q1'  # TODO: get quarter_index by current time
        self.fund_code = code  # 基金代码，需要初始化赋值
        self.fund_name = name  # 基金名称，需要初始化赋值
        self.morning_star_code = namecode  # 基金编码，晨星网特有，需要建立索引表

        self._morning_cookies = morning_cookies or None
        self._chrome_driver = chrome_driver or None
        self._is_trigger_catch = False
        self._catch_detail = None

        # 基本信息
        self.fund_cat = None  # 基金分类
        self.found_date = None  # 成立时间
        self.company = None  # 基金公司
        # 季度变动信息
        self.total_asset = None  # 总资产
        self.investname_style = None  # 投资风格
        self.manager = dict()  # 基金经理,name,id,管理时间
        self.three_month_retracement = 0.0  # 最差六个月回报
        self.june_month_retracement = 0.0  # 最差六个月回报
        self.bond_position = dict(
            {'total': '0.00'})  # 债券总仓位、前五大持仓
        self.stock_position = dict(
            {'total': '0.00'})  # 股票总仓位、前十大持仓
        self.risk_assessment = dict()  # 三年风险评估 -- 标准差 风险系数 夏普比
        self.risk_statistics = dict()  # 阿尔法 贝塔 R平方值
        self.risk_rating = dict()  # 风险评价 -- 二年、三年、五年、十年
        self.morning_star_rating = dict()  # 晨星评级--三年，五年，十年
        # 十大持仓信息
        self.ten_top_stock_list = []  # 股票十大持仓股信息
    # 处理基金详情页跳转

    def login_morning_star(self, cookie_str=None):
        login_url = 'https://www.morningstar.cn/membership/signin.aspx'
        if self._chrome_driver == None:
            from selenium import webdriver
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--no-sandbox")
            # _chrome_driver = webdriver.Chrome("/usr/local/chromedriver")
            self._chrome_driver = webdriver.Chrome(options=chrome_options)
            self._chrome_driver.set_page_load_timeout(12000)
            """
        模拟登录,支持两种方式：
            1. 设置已经登录的cookie
            2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
        """
        if cookie_str:
            set_cookies(self._chrome_driver,
                        login_url, cookie_str)
        else:
            if self._morning_cookies == None:
                login_status = login_site(
                    self._chrome_driver, login_url)
                if login_status:
                    print('login success')
                    sleep(3)
                else:
                    print('login fail')
                    exit()
                # 获取网站cookie
                _morning_cookies = self._chrome_driver.get_cookies()
            else:
                self._morning_cookies = self._chrome_driver.get_cookies()
                # print('cookies', self._morning_cookies)  # 打印设置成功的cookie
    # 更新基金信息，从晨星网上抓取，利用selinum原理

    def go_fund_url(self, cookie_str=None):
        self.login_morning_star(cookie_str)
        morning_fund_selector_url = "https://www.morningstar.cn/quicktake/" + \
            self.morning_star_code

        self._chrome_driver.get(morning_fund_selector_url)  # 打开爬取页面
        sleep(6)
        # 判断是否页面出错，重定向，如果是的话跳过
        if self._chrome_driver.current_url == 'https://www.morningstar.cn/errors/defaulterror.html':
            return False
        while self._chrome_driver.page_source == None:
            self._chrome_driver.refresh()
            print('wait:fund_code', self.fund_code)
            sleep(9)
            # self._chrome_driver.execute_script('location.reload()')

    def get_element_text_by_class_name(self, class_name, parent_id):
        try:
            text = self._chrome_driver.find_element_by_id(
                parent_id).find_element_by_class_name(class_name).text
            return text if text != '-' else None
        except NoSuchElementException:
            self._is_trigger_catch = True
            self._catch_detail = parent_id + '-' + class_name
            print('error_fund_info:', self.fund_code,
                  '-', self.morning_star_code, self.stock_position["total"])
            file_name = './abnormal/' + self.fund_code + \
                '-' + parent_id + "-no_such_element.png"
            # self._chrome_driver.save_screenshot(file_name)
            # driver.get_screenshot_as_file(file_name)
            # raise  # 抛出异常，注释后则不抛出异常
        return None

    def get_element_text_by_id(self, id):
        try:
            text = self._chrome_driver.find_element_by_id(
                id).text
            return text if text != '-' else None
        except NoSuchElementException:
            self._is_trigger_catch = True
            self._catch_detail = id
            print('error_fund_info:', self.fund_code,
                  '-', self.morning_star_code, self.stock_position["total"])
            file_name = './abnormal/' + '-' + id + self.fund_code + "-no_such_element.png"
            # self._chrome_driver.save_screenshot(file_name)
            # driver.get_screenshot_as_file(file_name)
            # raise  # 抛出异常，注释后则不抛出异常
        return None

    def get_element_text_by_xpath(self, xpath, parent_id=None, parent_el=None):
        try:
            text = '-'
            if parent_el == None:
                text = self._chrome_driver.find_element_by_xpath(xpath).text if parent_id == None else self._chrome_driver.find_element_by_id(
                    parent_id).find_element_by_xpath(xpath).text
            else:
                text = parent_el.find_element_by_xpath(xpath).text
            return text if text != '-' else None
        except NoSuchElementException:
            self._is_trigger_catch = True
            self._catch_detail = xpath
            print('error_fund_info:', self.fund_code,
                  '-', self.morning_star_code, self.stock_position["total"])
            file_name = './abnormal/' + \
                self.fund_code + '-' + xpath + "-no_such_element.png"
            # self._chrome_driver.save_screenshot(file_name)
            # driver.get_screenshot_as_file(file_name)
            # raise  # 抛出异常，注释后则不抛出异常
        return None

    def get_fund_base_info(self):
        # 基金分类
        self.fund_cat = self.get_element_text_by_class_name(
            "category", 'qt_base')
        # 成立时间
        self.found_date = self.get_element_text_by_class_name(
            "inception", 'qt_base')
        # 基金公司
        self.company = self.get_element_text_by_xpath(
            "//ul[@id='qt_management']/li[4]/span[@class='col2 comp']/a", 'qt_management')

    # 获取基金经理信息
    def get_fund_manager_info(self):
        try:
            # 基金经理
            manager_ele = self._chrome_driver.find_element_by_id(
                'qt_manager').find_element_by_xpath("ul")
            manager_name = manager_ele.find_element_by_xpath(
                "li[@class='col1']/a").text
            manager_id = re.findall(
                r'(?<=managerid=)(\w+)$',  manager_ele.find_element_by_xpath("li[@class='col1']/a").get_attribute('href')).pop(0)
            manager_start_date = manager_ele.find_element_by_xpath(
                "li[@class='col1']/i").text[0:10]
            manager_brife = manager_ele.find_element_by_xpath(
                "li[@class='col2']").text
            self.manager['id'] = manager_id
            self.manager['name'] = manager_name
            self.manager['start_date'] = manager_start_date
            self.manager['brife'] = manager_brife
        except NoSuchElementException:
            self._is_trigger_catch = True
            print('error_fund_info:', self.fund_code,
                  '-', self.morning_star_code)
            file_name = './abnormal/manager-' + self.fund_code + "-no_such_element.png"
            # self._chrome_driver.save_screenshot(file_name)
            # driver.get_screenshot_as_file(file_name)
            # raise  # 抛出异常，注释后则不抛出异常
        return None

    def get_fund_morning_rating(self):
        try:
            qt_el = self._chrome_driver.find_element_by_id('qt_star')
            rating_3_src = qt_el.find_element_by_xpath(
                "//li[@class='star3']/img").get_attribute('src')
            rating_5_src = qt_el.find_element_by_xpath(
                "//li[@class='star5']/img").get_attribute('src')
            rating_10_src = qt_el.find_element_by_xpath(
                "//li[@class='star10']/img").get_attribute('src')
            rating_3 = get_star_count(rating_3_src)
            rating_5 = get_star_count(rating_5_src)
            rating_10 = get_star_count(rating_10_src)
            self.morning_star_rating[3] = rating_3
            self.morning_star_rating[5] = rating_5
            self.morning_star_rating[10] = rating_10
        except NoSuchElementException:
            self._is_trigger_catch = True
            print('error_fund_info:', self.fund_code,
                  '-', self.morning_star_code)
            file_name = './abnormal/morning_rating-' + \
                self.fund_code + "-no_such_element.png"
    # 风险评级

    def get_fund_qt_rating(self):
        try:
            qt_el = self._chrome_driver.find_element_by_id('qt_rating')
            rating_2_src = qt_el.find_element_by_xpath(
                "//li[5]/img").get_attribute('src')
            rating_3_src = qt_el.find_element_by_xpath(
                "li[6]/img").get_attribute('src')
            rating_5_src = qt_el.find_element_by_xpath(
                "li[7]/img").get_attribute('src')
            rating_10_src = qt_el.find_element_by_xpath(
                "li[8]/img").get_attribute('src')
            # //*[@id="qt_rating"]/li[6]/img
            rating_2 = re.findall(
                r"\d(?:stars\.gif)$", rating_2_src)[0][0]
            rating_3 = re.findall(
                r"\d(?:stars\.gif)$", rating_3_src)[0][0]
            rating_5 = re.findall(
                r"\d(?:stars\.gif)$", rating_5_src)[0][0]
            rating_10 = re.findall(
                r"\d(?:stars\.gif)$", rating_10_src)[0][0]
            self.risk_rating[2] = rating_2
            self.risk_rating[3] = rating_3
            self.risk_rating[5] = rating_5
            self.risk_rating[10] = rating_10
        except NoSuchElementException:
            self._is_trigger_catch = True
            print('error_fund_info:', self.fund_code,
                  '-', self.morning_star_code)
            file_name = './abnormal/qt_rating-' + self.fund_code + "-no_such_element.png"

    def get_fund_season_info(self):
        # 总资产  TODO: 增加一个数据更新时间field
        self.total_asset = self.get_element_text_by_class_name(
            "asset", 'qt_base')
        # 投资风格
        self.investname_style = self.get_element_text_by_class_name(
            'sbdesc', 'qt_base')
        # 最差三个月回报
        self.three_month_retracement = self.get_element_text_by_class_name(
            "r3", 'qt_worst')
        # 最差六个月回报
        self.june_month_retracement = self.get_element_text_by_class_name(
            "r6", 'qt_worst')
        # 获取股票总仓位、前十大持仓、债券总仓位、前五大持仓 TODO: 增加一个数据更新时间field
        total = self.get_element_text_by_class_name(
            "stock", 'qt_asset')
        self.stock_position["total"] = total if total != None else '0.00'
        # self.total["total"] = float(
        #     total) / 100 if total != '-' else None  # 股票的总仓位
        self.bond_position["total"] = self.get_element_text_by_class_name(
            "bonds", 'qt_asset')

        # 十大股票仓位
        ten_stock_position = None
        ten_stock_position_text = self.get_element_text_by_id("qt_stocktab")
        if ten_stock_position_text != None or ten_stock_position_text != '-':
            ten_stock_position_list = re.findall(
                r"\d+\.?\d*", ten_stock_position_text)
            if len(ten_stock_position_list) > 0:
                ten_stock_position = ten_stock_position_list.pop(0)
        self.stock_position["ten"] = ten_stock_position

        # 五大债券仓位
        five_bond_position = None
        five_bond_position_text = self.get_element_text_by_id("qt_bondstab")
        if five_bond_position_text != None or five_bond_position_text != '-':
            five_bond_position_list = re.findall(
                r"\d+\.?\d*", five_bond_position_text)
            if len(five_bond_position_list) > 0:
                five_bond_position = five_bond_position_list.pop(0)
        self.bond_position["five"] = five_bond_position

        # 获取标准差
        # standard_deviation = self._chrome_driver.find_element_by_id(
        #     "qt_risk").find_element_by_xpath('li[16]').text
        #  TODO: 增加一个数据更新时间field
        standard_deviation = self.get_element_text_by_xpath(
            'li[16]', 'qt_risk')
        if standard_deviation != None:
            self.risk_assessment["standard_deviation"] = standard_deviation
            # 获取风险系数
            risk_coefficient = self.get_element_text_by_xpath(
                'li[23]', 'qt_risk')
            self.risk_assessment["risk_coefficient"] = risk_coefficient
            # 获取夏普比
            sharpby = self.get_element_text_by_xpath(
                'li[30]', 'qt_risk')
            self.risk_assessment["sharpby"] = sharpby
            # 获取阿尔法
            alpha = self.get_element_text_by_xpath(
                'li[5]', 'qt_riskstats')
            self.risk_statistics["alpha"] = alpha
            # 获取贝塔
            beta = self.get_element_text_by_xpath(
                'li[8]', 'qt_riskstats')
            self.risk_statistics["beta"] = beta
            # 获取R平方
            r_square = self.get_element_text_by_xpath(
                'li[11]', 'qt_riskstats')
            self.risk_statistics["r_square"] = r_square
    # 获取持仓

    def get_asset_composition_info(self):
        # 判断是否含有股票持仓
        li_elements = self._chrome_driver.find_element_by_id(
            'qt_stock').find_elements_by_xpath("li")
        for index in range(4, len(li_elements) - 1, 4):
            temp_stock_info = dict()  # 一只股票信息
            stock_base = li_elements[index].text.split('.')
            temp_stock_info['stock_code'] = stock_base[0]
            temp_stock_info['stock_market'] = None if len(
                stock_base) == 1 else stock_base.pop()
            temp_stock_info['stock_name'] = li_elements[index+1].text
            # temp_stock_info['stock_value'] = li_elements[index+2].text
            temp_stock_info['stock_portion'] = li_elements[index +
                                                           3].text if li_elements[index+3].text != '-' else None
            self.ten_top_stock_list.append(temp_stock_info)
