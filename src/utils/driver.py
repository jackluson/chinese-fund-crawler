'''
Desc:
File: /driver.py
File Created: Tuesday, 1st November 2022 10:38:28 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver


def create_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(12000)
    return chrome_driver



def text_to_be_present_in_element(locator, text, next_page_locator):
    """ An expectation for checking if the given text is present in the
    specified element.
    locator, text -- 判读是否当前页一致，没有的话，切换上一页，下一页操作
    """
    def _predicate(driver):
        try:
            element_text = driver.find_element(By.XPATH, locator).text
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

