'''
Desc:
File: /manager.py
Project: models
File Created: Thursday, 25th August 2022 10:21:22 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys

sys.path.append('./src')
from sqlalchemy import (BigInteger, Column, Date, DateTime, ForeignKey,
                        Integer, String, Table, UniqueConstraint, func, text)
from sqlalchemy.orm import registry, relationship

from lib.mysnowflake import IdWorker
from models.var import Model, ORM_Base, engine, prefix

manager_table_name = prefix + 'manager'
manager_table = Table(manager_table_name, ORM_Base.metadata, autoload=True, autoload_with=engine)

idWorker = IdWorker()
class Manager(ORM_Base, Model):
    __table__ = manager_table
    # managerAssoc = relationship("ManagerAssoc", back_populates="manager")

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
        return f"Manager(id={self.id!r}, name={self.name!r}, manager_id={self.manager_id!r})"

class ManagerAssoc(ORM_Base, Model):
    __tablename__ = prefix + 'manager_assoc'
    id = Column(BigInteger, primary_key=True)
    quarter_index = Column(String(12))
    manager_key = manager_table_name + '.manager_id'
    manager_id = Column(String(32), ForeignKey(manager_key), nullable=False)
    fund_code_key = prefix + 'base' + '.fund_code'
    fund_code= Column(String(10), ForeignKey(fund_code_key), nullable=False)
    manager_start_date = Column(Date(), nullable=False)
    update_time = Column(DateTime,  server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), onupdate=func.now()) 
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

    UniqueConstraint(quarter_index, manager_id, fund_code, name='uix_1')

    manager = relationship('Manager', backref='manager_assoc')
    # fund_base = relationship("Fund", backref="manager_assoc")
    def __init__(self, **kwargs):
        self.id = idWorker.get_id()
        ORM_Base.__init__(self, **kwargs)
        Model.__init__(self, **kwargs, id = self.id)

    def __repr__(self):
        return f"ManagerAssoc(id={self.id!r}, name={self.manager_id!r}, fullname={self.fund_code!r})"

def create():
    ORM_Base.metadata.create_all(engine)
    # mapper_registry.metadata.create_all(engine)
    # ManagerAssoc.__table__.drop(engine)

def drop():
    ManagerAssoc.__table__.drop(engine)

if __name__ == '__main__':
    create()
    # drop()
