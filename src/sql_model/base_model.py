'''
Desc: 基础sql 类
File: /base_model.py
Project: sql_model
File Created: Tuesday, 10th August 2021 12:35:02 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

from db.connect import connect
from utils.index import get_last_quarter_str, get_quarter_date


class BaseModel(object):

    def __init__(self):
        self.quarter_index = get_last_quarter_str()
        self.quarter_date = get_quarter_date(self.quarter_index)
        connect_instance = connect()
        self.connect_instance = connect_instance
        self.cursor = connect_instance.cursor()
