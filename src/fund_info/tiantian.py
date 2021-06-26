'''
Desc: 天天基金信息爬取
File: /tiantian.py
Project: fund_info
File Created: Tuesday, 1st June 2021 11:02:59 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import requests
from selenium import webdriver


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--headless')
chrome_driver = webdriver.Chrome(options=chrome_options)

def get_tiantian_fund_list(chrome_driver):
  fund_list_url = "http://fund.eastmoney.com/js/fundcode_search.js"

  # res = requests.get(fund_list_url)  # 自动编码
  # # print("res", res.text)

  chrome_driver.get(fund_list_url)
  fund_list_code_str =  chrome_driver.find_element_by_tag_name("pre").text
  return_value_code_str = ";return {\
                            fund_list: r \
                            };"
  execute_return_list = chrome_driver.execute_script(fund_list_code_str + return_value_code_str)
# execute_return_list = chrome_driver.execute_script(";return r;")
# print("execute_return", execute_return_list.get('fund_list')[0])

 
return_value_code_str = ";return {\
                          data_holder_structure: Data_holderStructure \
                          };"
item_fund_info_url = "http://fund.eastmoney.com/pingzhongdata/000001.js"
# res = requests.get(item_fund_info_url)  # 自动编码
# # print("res", res.text)
chrome_driver.get(item_fund_info_url)

content_text = chrome_driver.page_source



fund_item_code_str =  chrome_driver.find_element_by_tag_name("pre").text

execute_return_item = chrome_driver.execute_script(fund_item_code_str + return_value_code_str)
print("execute_return", execute_return_item)
# global_var = chrome_driver.execute_script("return window;")
# print("global_var", global_var)

# chrome_driver.execute_script("return globalVar;")
