
from urllib import parse
import time
import os


def parse_cookiestr(cookie_str, split_str="; "):
    cookielist = []
    for item in cookie_str.split(split_str):
        cookie = {}
        itemname = item.split('=')[0]
        iremvalue = item.split('=')[1]
        cookie['name'] = itemname
        cookie['value'] = parse.unquote(iremvalue)
        cookielist.append(cookie)
    return cookielist


def set_cookies(chrome_driver, url, cookie_str):
    chrome_driver.get(url)
    # 2.需要先获取一下url，不然使用add_cookie会报错，这里有点奇怪
    cookie_list = parse_cookiestr(cookie_str)
    chrome_driver.delete_all_cookies()
    for i in cookie_list:
        cookie = {}
        # 3.对于使用add_cookie来说，参考其函数源码注释，需要有name,value字段来表示一条cookie，有点生硬
        cookie['name'] = i['name']
        cookie['value'] = i['value']
        # 4.这里需要先删掉之前那次访问时的同名cookie，不然自己设置的cookie会失效
        # chrome_driver.delete_cookie(i['name'])
        # 添加自己的cookie
        # print('cookie', cookie)
        chrome_driver.add_cookie(cookie)
    chrome_driver.refresh()


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


def get_star_count(morning_star_url):
    import numpy as np
    import requests
    from PIL import Image
    module_path = os.path.dirname(__file__)
    temp_star_url = module_path + '/assets/star/tmp.gif'
    r = requests.get(morning_star_url)
    with open(temp_star_url, "wb") as f:
        f.write(r.content)
    f.close()
    path = module_path + '/assets/star/star'

    # path = './assets/star/star'
    for i in range(6):
        p1 = np.array(Image.open(path+str(i)+'.gif'))
        p2 = np.array(Image.open(temp_star_url))
        if (p1 == p2).all():
            return i


def login_site(chrome_driver, site_url, redirect_url=None):
    site_url = site_url if redirect_url == None else site_url + \
        '?ReturnUrl=' + redirect_url
    chrome_driver.get(site_url)
    time.sleep(2)
    from selenium.webdriver.support import expected_conditions as EC
    username = chrome_driver.find_element_by_id('emailTxt')
    password = chrome_driver.find_element_by_id('pwdValue')
    check_code = chrome_driver.find_element_by_id('txtCheckCode')
    username.send_keys('18219112108@163.com')
    password.send_keys('w780880')
    count = 1
    flag = True
    while count < 10 and flag:
        code = identify_verification_code(chrome_driver)
        check_code.clear()
        time.sleep(1)
        check_code.send_keys(code)
        time.sleep(3)
        submit = chrome_driver.find_element_by_id('loginGo')
        submit.click()
        # 通过弹窗判断验证码是否正确
        time.sleep(3)
        from selenium.webdriver.common.by import By
        # message_container = chrome_driver.find_element_by_id('message-container')
        try:
            message_box = chrome_driver.find_element_by_id(
                'message-container')
            flag = message_box.is_displayed()
            if flag:
                close_btn = message_box.find_element(
                    By.CLASS_NAME, "modal-close")
                close_btn.click()
                time.sleep(1)
            print('flag', flag)

        except:
            return True

    if count > 10:
        return False
    return True


def parse_csv(datafile):
    data = []
    with open(datafile, "r") as f:
        header = f.readline().split(",")  # 获取表头
        counter = 0
        for line in f:
            if counter == 10:
                break
            fields = line.split(",")
            entry = {}
            for i, value in enumerate(fields):
                entry[header[i].strip()] = value.strip()  # 用strip方法去除空白
            data.append(entry)
            counter += 1

    return data
