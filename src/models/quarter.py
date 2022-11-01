'''
Desc: 季度时间
File: /quarter.py
Project: models
File Created: Sunday, 28th August 2022 9:21:25 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
sys.path.append('./src')
from datetime import datetime
from sqlalchemy import UniqueConstraint, Column, text, Integer, String, Date, DateTime, Enum, func
from sqlalchemy.orm import validates, Session
from models.var import ORM_Base, engine, Model


class Quarter(ORM_Base, Model):
    __tablename__ = 'quarter'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    quarter_index = Column(String(12), nullable=False, unique=True)
    start_time = Column(Date(), nullable=False, unique=True)
    end_time = Column(Date(), nullable=False, unique=True)
    update_time = Column(DateTime,  server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), onupdate=func.now()) 
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    UniqueConstraint(quarter_index, name='uix_1')

    def __init__(self, *args, **kwargs) -> None:
        column_keys = self.__table__.columns.keys()
        udpate_data = dict()
        for key in kwargs.keys():
            if key not in column_keys:
                continue
            else:
                udpate_data[key] = kwargs[key]
        ORM_Base.__init__(self, **udpate_data)
        Model.__init__(self, **kwargs, id = self.id)


    @validates('end_time')
    def validate_start_time(self, key, end_time):
        end_time_stamp =  datetime.strptime (end_time, '%Y-%m-%d')
        start_time_stamp = datetime.strptime (self.start_time, '%Y-%m-%d')
        if end_time_stamp > start_time_stamp:
            return end_time
        else:
            assert 'end_time cannot less than start_time' in end_time
        return end_time

    def __repr__(self):
        return f"Quarter(name={self.quarter_index!r})"

def create():
    ORM_Base.metadata.create_all(engine)

def drop():
    Quarter.__table__.drop(engine)

if __name__ == '__main__':
    # drop()
    create()
