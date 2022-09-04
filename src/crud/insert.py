'''
Desc:
File: /insert.py
Project: crud
File Created: Sunday, 28th August 2022 11:21:42 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''

import sys
sys.path.append('./src')

from sqlalchemy.orm import Session
from models.manager import Manager, ManagerAssoc
from models.quarter import Quarter
from models.var import prefix, ORM_Base, engine

session = Session(engine)

def add_quarter(year):
    boundary_date_list = ['03-31', '06-30', '09-30', '12-31']
    date_list_len = len(boundary_date_list)
    quarter_list = []
    for i in range(date_list_len):
        cur_year = year if i != 0 else str(int(year) - 1)
        start_index = i - 1 if i - 1 >= 0 else date_list_len - i - 1
        start_date = boundary_date_list[start_index]
        end_date = boundary_date_list[i]
        quarter_data = {
            'quarter_index': year +  "-Q" +  str(i + 1),
            'start_time': cur_year + '-' + start_date,
            'end_time': year + '-' + end_date
        }
        quarter = Quarter(**quarter_data)
        # quarter.save()
        # session.add(quarter)
        quarter_list.append(quarter)
    session.add_all(quarter_list)
    session.commit()



if __name__ == '__main__':
    year = '2023'
    # add_quarter(year)
    manager_data = {
        # 'id': 12,
        'manager_start_date': '2022-09-03',
        'name': 'sdfsd23fs',
        'brife': 'sdfsdfs',
        'manager_id': '22323343'
    }
    manager = Manager(**manager_data)
    # manager2 = Manager(**manager_data2)
    manager_assoc_data = {
        # 'id': 12,
        'quarter_index': '2022-Q3',
        'manager_start_date': '2022-09-03',
        'manager_id': manager_data['manager_id'],
        'fund_code': "000001"
    }
    # manager.save()
    manager.upsert(ingore_keys = ['manager_id'])
    # manager_assoc = ManagerAssoc(**manager_assoc_data)
    # print("manager_assoc", manager_assoc)
    # manager_assoc.upsert(ingore_keys = ['manager_id'])
    # manager_assoc.upsert()
    # manager.upsert(ingore_keys = ['manager_id'])


