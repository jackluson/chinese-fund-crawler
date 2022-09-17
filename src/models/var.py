'''
Desc: 变量配置
File: /config.py
Project: models
File Created: Saturday, 27th August 2022 12:20:04 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
sys.path.append('./src')
from sqlalchemy import Column, text, DateTime, func
from sqlalchemy.dialects.mysql import insert
from db.engine import get_engine, get_orm_base

from sqlalchemy.orm import Session

ORM_Base = get_orm_base()

prefix = 'fund_morning_'

engine = get_engine(echo=False)

# class ORM_Base(Base):
#     def __init__(self, **kwargs) -> None:
#         column_keys = self.__table__.columns.keys()
#         udpate_data = dict()
#         for key in kwargs.keys():
#             if key not in column_keys:
#                 continue
#             else:
#                 udpate_data[key] = kwargs[key]
        # Base.__init__(self, **udpate_data)


class Model():
    __input_data__ = dict()

    def __init__(self, **kwargs) -> None:
        self.__input_data__ = kwargs
        self.session = Session(engine)

    def save(self):
        self.session.add(self)
        self.session.commit()
    
    def upsert(self, *, ingore_keys = []):
        column_keys = self.__table__.columns.keys()

        udpate_data = dict()
        for key in self.__input_data__.keys():
            if key not in column_keys:
                continue
            else:
                udpate_data[key] = self.__input_data__[key]

        insert_stmt = insert(self.__table__).values(**udpate_data)

        all_ignore_keys = ['id']
        if isinstance(ingore_keys, list):
            all_ignore_keys =[*all_ignore_keys, *ingore_keys]
        else:
            all_ignore_keys.append(ingore_keys)

        udpate_columns = dict()
        for key in self.__input_data__.keys():
            if key not in column_keys or key in all_ignore_keys:
                continue
            else:
                udpate_columns[key] = insert_stmt.inserted[key]
        
        on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
            **udpate_columns
        )
        # self.session.add(self)
        self.session.execute(on_duplicate_key_stmt)
        self.session.commit()


