'''
Desc: 变量配置
File: /config.py
Project: models
File Created: Saturday, 27th August 2022 12:20:04 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
from db.engine import get_engine, get_orm_base

ORM_Base = get_orm_base()

prefix = 'fund_morning_'

engine = get_engine(echo=True)
