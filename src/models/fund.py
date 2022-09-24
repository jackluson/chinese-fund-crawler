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
from sqlalchemy.orm import relationship

from sqlalchemy import Table
from models.var import prefix, ORM_Base, engine

fund_base_tablename = prefix + 'base'
fund_quarter_tablename = prefix + 'quarter'

fund_base_table = Table(fund_base_tablename, ORM_Base.metadata, autoload=True, autoload_with=engine)
fund_quarter_table = Table(fund_quarter_tablename, ORM_Base.metadata, autoload=True, autoload_with=engine)

class FundBase(ORM_Base):
    __table__ = fund_base_table

    def __repr__(self):
        return f"Fund Base(id={self.id!r}, name={self.fund_code!r}, manager_id={self.fund_name!r})"


class FundQuarter(ORM_Base):
    __table__ = fund_quarter_table
    fund = relationship('FundBase', backref='fund_quarter')

    def __repr__(self):
        return f"Fund {fund_quarter_tablename}(id={self.id!r}, name={self.fund_code!r})"
