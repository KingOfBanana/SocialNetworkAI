# coding:utf-8

from db.basic_db import proxy_db_session
from db.models import Proxys
from decorators.decorator import db_commit_decorator

def count_proxy():
	results = proxy_db_session.query(Proxys).count()