'''
Desc: insert 相关
File: /fund_insert.py
Project: sql_model
File Created: Monday, 10th May 2021 2:01:55 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from threading import Lock
from db.connect import connect


class FundInsert:
    def __init__(self):
        connect_instance = connect()
        self.connect_instance = connect_instance
        self.cursor = connect_instance.cursor()
        self.lock = Lock()

    def generate_insert_sql(self, target_dict, table_name, ignore_list):
        keys = ','.join(target_dict.keys())
        values = ','.join(['%s'] * len(target_dict))
        update_values = ''
        for key in target_dict.keys():
            if key in ignore_list:
                continue
            update_values = update_values + '{0}=VALUES({0}),'.format(key)
        sql_insert = "INSERT INTO {table} ({keys}) VALUES ({values})  ON DUPLICATE KEY UPDATE {update_values}; ".format(
            table=table_name,
            keys=keys,
            values=values,
            update_values=update_values[0:-1]
        )
        return sql_insert
