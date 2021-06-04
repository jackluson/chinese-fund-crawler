'''
Desc: 更新基金一些信息，例如是否清盘
File: /fund_update.py
Project: sql_model
File Created: Thursday, 3rd June 2021 3:13:40 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''


from fund_info.supplement import FundSupplement


if __name__ == '__main__':
  fund_supplement = FundSupplement()
  fund_supplement.update_archive_status()
