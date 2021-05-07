
import pymysql
import os
from dotenv import load_dotenv


def connect():
    load_dotenv()
    env_db_host = os.getenv('db_host')
    env_db_name = os.getenv('db_name')
    env_db_user = os.getenv('db_user')
    env_db_password = os.getenv('db_password')
    connect = pymysql.connect(
        host=env_db_host, user=env_db_user, password=env_db_password, db=env_db_name, charset='utf8')
    return connect


if __name__ == '__main__':
    connect()
