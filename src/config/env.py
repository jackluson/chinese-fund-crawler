'''
Desc:
File: /config.py
Project: config
File Created: Sunday, 14th August 2022 5:57:02 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import os

from dotenv import load_dotenv
load_dotenv()

env_db_host = os.getenv('db_host')
env_db_port = os.getenv('db_port')
env_db_name = os.getenv('db_name')

env_db_user = os.getenv('db_user')
env_db_password = os.getenv('db_password')

env_db_stock_name = os.getenv('db_stock_name')
