'''
Desc:
File: /ddl.py
Project: crud
File Created: Monday, 29th August 2022 10:23:08 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
sys.path.append('./src')
from sqlalchemy import text
from models.var import prefix, ORM_Base, engine


def alter_foreign_quarter():
    with engine.connect() as conn:
        table = 'fund_morning_quarter'
        source_table = 'quarter'
        table_data = {
            "table": table,
            "target_key": 'quarter_index',
            'source_table': source_table,
            'foreign_name': table + '_fk_' + source_table,
            'source_key': 'quarter_index'
        }
        sql = "ALTER TABLE {table} ADD CONSTRAINT {foreign_name} FOREIGN KEY ({target_key}) REFERENCES {source_table}({source_key})".format(**table_data)
        conn.execute(text(sql))
        conn.commit()

if __name__ == '__main__':
    alter_foreign_quarter()

