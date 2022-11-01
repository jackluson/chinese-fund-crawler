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
from sqlalchemy.orm import relationship

from lib.mysnowflake import IdWorker
from models.var import Model, ORM_Base, engine, prefix

fund_base_tablename = prefix + 'base'
fund_quarter_tablename = prefix + 'quarter'

fund_base_table = Table(fund_base_tablename, ORM_Base.metadata, autoload=True, autoload_with=engine)
fund_quarter_table = Table(fund_quarter_tablename, ORM_Base.metadata, autoload=True, autoload_with=engine)

idWorker = IdWorker()

class FundBase(ORM_Base, Model):
    __table__ = fund_base_table

    def __init__(self, **kwargs):
        self.id = idWorker.get_id()
        column_keys = self.__table__.columns.keys()
        udpate_data = dict()
        for key in kwargs.keys():
            if key not in column_keys:
                continue
            else:
                udpate_data[key] = kwargs[key]
        ORM_Base.__init__(self, **udpate_data)
        Model.__init__(self, **kwargs, id = self.id)

    def __repr__(self):
        return f"Fund Base(id={self.id!r}, name={self.fund_code!r}, manager_id={self.fund_name!r})"


class FundQuarter(ORM_Base):
    __table__ = fund_quarter_table
    fund = relationship('FundBase', backref='fund_quarter')

    def __repr__(self):
        return f"Fund {fund_quarter_tablename}(id={self.id!r}, name={self.fund_code!r})"
