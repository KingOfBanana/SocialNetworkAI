# coding:utf-8
from sqlalchemy import text
from db.basic_db import db_session
from db.models import WeiboPic
from decorators.decorator import db_commit_decorator

@db_commit_decorator
def insert_weibo_pics(weibo_pics):
    for pic in weibo_pics:
        db_session.add(pic)
    db_session.commit()