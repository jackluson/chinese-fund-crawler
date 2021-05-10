'''
Desc: cookies 相关
File: /cookies.py
Project: utils
File Created: Monday, 10th May 2021 12:39:56 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from urllib import parse


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
