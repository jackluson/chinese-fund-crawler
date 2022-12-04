
import pymysql
from config.env import env_db_host, env_db_name, env_db_user, env_db_password, env_db_stock_name

def connect():
    connect = pymysql.connect(
        host=env_db_host, user=env_db_user, password=env_db_password, db=env_db_name, charset='utf8')
    return connect


def connect_dict():
    connect = pymysql.connect(
        host=env_db_host, user=env_db_user, password=env_db_password, db=env_db_stock_name,
        charset='utf8')
    connect_dict = {
        'connect': connect,
        'cursor': connect.cursor(),
        'dict_cursor': connect.cursor(pymysql.cursors.DictCursor)
    }
    return connect_dict


if __name__ == '__main__':
    connect()
