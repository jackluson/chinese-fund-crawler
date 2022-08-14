'''
Desc:
File: /engine.py
Project: db
File Created: Sunday, 14th August 2022 5:41:01 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import os
import sys
sys.path.append(os.getcwd() + '/src')

from sqlalchemy import create_engine, text
from config.env import env_db_host, env_db_name, env_db_user, env_db_password, env_db_port

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + env_db_user + ':'+ env_db_password +'@'+ env_db_host + ':' + env_db_port + '/' + env_db_name

_global_engine = None

def get_engine():
    global _global_engine 
    if _global_engine == None:
        _global_engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True, future=True)
    return _global_engine

if __name__ == '__main__':
    engine1 = get_engine()
    with engine1.connect() as conn:
        query = {"fund_code": '000696'}
        result = conn.execute(
            text("SELECT * FROM fund_morning_snapshot WHERE fund_code = :fund_code"),
            query
        )
        for row in result:
            print("row", row)
