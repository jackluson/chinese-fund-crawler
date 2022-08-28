'''
Desc:
File: /fund.py
Project: models
File Created: Saturday, 27th August 2022 11:47:51 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
sys.path.append('./src')

from sqlalchemy import Table
from models.var import prefix, ORM_Base, engine

fund_table_base = prefix + 'base'

fund_table = Table(fund_table_base, ORM_Base.metadata, autoload=True, autoload_with=engine)

class Fund(ORM_Base):
    __table__ = fund_table

    def __repr__(self):
        return f"Fund Base(id={self.id!r}, name={self.fund_code!r}, manager_id={self.fund_name!r})"
