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

from sqlalchemy.orm import Session, registry, relationship, aliased
from sqlalchemy import DATE, MetaData, Table, Column, Integer, BigInteger, String, ForeignKey, select
from db.engine import get_engine
from models.var import prefix, ORM_Base, engine

manager_table_name = prefix + 'manager'
manager_table = Table(manager_table_name, ORM_Base.metadata, autoload=True, autoload_with=engine)

class Manager(ORM_Base):
    __table__ = manager_table
    # managerAssoc = relationship("ManagerAssoc", back_populates="manager")
    def __repr__(self):
        return f"Manager(id={self.id!r}, name={self.name!r}, manager_id={self.manager_id!r})"

class ManagerAssoc(ORM_Base):
    __tablename__ = prefix + 'manager_assoc'
    manager_key = manager_table_name + '.manager_id'
    id = Column(BigInteger, primary_key=True)
    quarter_index = Column(String(12))
    manager_id = Column(String(32), ForeignKey(manager_key))
    fund_code_key = prefix + 'base' + '.fund_code'
    fund_code= Column(String(10), ForeignKey(fund_code_key))
    # manager = relationship('Manager', backref='manager_assoc')
    # fund_base = relationship("Fund", backref="manager_assoc")

    def __repr__(self):
        return f"ManagerAssoc(id={self.id!r}, name={self.manager_id!r}, fullname={self.fund_code_id!r})"

def create():
    ORM_Base.metadata.create_all(engine)
    # mapper_registry.metadata.create_all(engine)
    # ManagerAssoc.__table__.drop(engine)


if __name__ == '__main__':
    create()
    # demo()
