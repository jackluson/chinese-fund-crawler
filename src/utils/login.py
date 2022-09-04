'''
Desc: 登录
File: /login.py
Project: utils
File Created: Monday, 10th May 2021 12:29:35 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import time
import os
from dotenv import load_dotenv

from .cookies import set_cookies

load_dotenv()


# 二维码识别
def identify_verification_code(chrome_driver, id="checkcodeImg"):
    # 生成年月日时分秒时间
    picture_time = time.strftime(
        "%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    # 获取到当前文件的目录，并检查是否有 directory_time 文件夹，如果不存在则自动新建 directory_time 文件
    try:
        file_Path = os.getcwd() + '/code-record/' + directory_time + '/'
        if not os.path.exists(file_Path):
            os.makedirs(file_Path)
            print("目录新建成功：%s" % file_Path)
        else:
            print("目录已存在！！！")
    except BaseException as msg:
        print("新建目录失败：%s" % msg)
    try:
        from selenium.webdriver.common.by import By
        ele = chrome_driver.find_element(By.ID, id)
        code_path = './code-record/' + directory_time + '/' + picture_time + '_code.png'
        url = ele.screenshot(code_path)
        if url:
            print("%s ：截图成功！！！" % url)
            from PIL import Image
            image = Image.open(code_path)
            # image.show()
            import pytesseract
            custom_oem_psm_config = '--oem 0 --psm 13 digits'
            identify_code = pytesseract.image_to_string(
                image, config=custom_oem_psm_config)
            code = "".join(identify_code.split())
            return code
        else:
            raise Exception('截图失败,不能保存')
    except Exception as pic_msg:
        print("截图失败：%s" % pic_msg)


# 模拟手动输入账号密码登录
def mock_login_site(chrome_driver, site_url, redirect_url=None):
    site_url = site_url if redirect_url == None else site_url + \
        '?ReturnUrl=' + redirect_url
    chrome_driver.get(site_url)
    time.sleep(2)
    from selenium.webdriver.support import expected_conditions as EC
    username = chrome_driver.find_element_by_id('emailTxt')
    password = chrome_driver.find_element_by_id('pwdValue')
    env_username = os.getenv('morning_star_username')
    env_password = os.getenv('morning_star_password')
    username.send_keys(env_username)
    password.send_keys(env_password)
    submit = chrome_driver.find_element_by_id('loginGo')
    submit.click()
    # check_code = chrome_driver.find_element_by_id('txtCheckCode')
    # count = 1
    # flag = True
    # while count < 10 and flag:
    #     code = identify_verification_code(chrome_driver)
    #     check_code.clear()
    #     time.sleep(1)
    #     check_code.send_keys(code)
    #     time.sleep(3)
    #     submit = chrome_driver.find_element_by_id('loginGo')
    #     submit.click()
    #     # 通过弹窗判断验证码是否正确
    #     time.sleep(3)
    #     from selenium.webdriver.common.by import By
    #     # message_container = chrome_driver.find_element_by_id('message-container')
    #     try:
    #         message_box = chrome_driver.find_element_by_id(
    #             'message-container')
    #         flag = message_box.is_displayed()
    #         if flag:
    #             close_btn = message_box.find_element(
    #                 By.CLASS_NAME, "modal-close")
    #             close_btn.click()
    #             time.sleep(1)
    #         print('flag', flag)

    #     except:
    #         return True

    # if count > 10:
    #     return False
    time.sleep(5)
    return True


def login_morning_star(redirect_url, is_cookies_login=False):
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--headless')
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(12000)
    """
    模拟登录,支持两种方式：
        1. 设置已经登录的cookie
        2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
    """
    login_url = 'https://www.morningstar.cn/membership/signin.aspx'
    cookie_str = os.getenv('login_cookie')
    if is_cookies_login and cookie_str:
        target_url = redirect_url if redirect_url else login_url
        set_cookies(chrome_driver, target_url, cookie_str)
    else:
        login_status = mock_login_site(
            chrome_driver, login_url, redirect_url)
        if login_status:
            print('login success')
        else:
            print('login fail')
            exit()
    return chrome_driver
