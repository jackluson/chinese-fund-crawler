'''
Desc: 更新基金一些信息，例如是否清盘
File: /fund_update.py
Project: sql_model
File Created: Thursday, 3rd June 2021 3:13:40 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import time
from utils.index import get_quarter_index
from db.connect import connect

class FundUpdate:
    def __init__(self, code=None):
      self.fund_code = code
      last_quarter_time = time.localtime(time.time() - 3 * 30 * 24 * 3600)
      year = time.strftime("%Y", last_quarter_time)
      date = time.strftime("%m-%d", last_quarter_time)
      index = get_quarter_index(date)
      quarter_index = year + '-Q' + str(index)
      self.quarter_index = quarter_index
      connect_instance = connect()
      self.connect_instance = connect_instance
      self.cursor = connect_instance.cursor()

    def update_archive_status(self, archive_value=0, *, fund_code=None):
      code = fund_code
      if fund_code == None:
          code = self.fund_code
      if archive_value == 0:
        print(code, '本来为0')
        return
      sql_update_archive = "UPDATE fund_morning_base SET is_archive = %s WHERE fund_code = %s;"
      self.cursor.execute(sql_update_archive, (archive_value, code))
      self.connect_instance.commit()
