# coding:utf-8
from db.basic_db import proxy_db_session
from db.models import Proxys
from decorators.decorator import db_commit_decorator
from sqlalchemy import func

@db_commit_decorator
def insert_proxy(proxies):
	if proxies:
	    for proxy in proxies:
	    	if proxy:
	        	proxy_db_session.add(proxy)
	    proxy_db_session.commit()

@db_commit_decorator
def count_proxy():
	cnt = (proxy_db_session.query(func.count(Proxys.id)).first())[0]
	if type(cnt) == int:
		return cnt
	else:
		return 0

# 正常情况下如果count>num，返回num条，否则返回count条，其他情况返回空数组
# 在这里只寻找https代理
@db_commit_decorator
def fetch_proxy(status = 1, num = 1):
	if num <= 0:
		return []
	count = count_proxy()
	result = []
	if status == 1:
		if count >= num:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 0).order_by(Proxys.score, Proxys.speed).limit(num).all()
		elif count > 0:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 0).order_by(Proxys.score, Proxys.speed).limit(count).all()
	elif status == 0:
		if count >= num:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 1).order_by(Proxys.score, Proxys.speed).limit(num).all()
		elif count > 0:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 1).order_by(Proxys.score, Proxys.speed).limit(count).all()
	if not result and result != []:
		result = []
	return result
	

@db_commit_decorator
def get_proxy_by_dict(proxy_dict):
	if not proxy_dict:
		return None
	value = proxy_dict.get('http')
	if value:
		value = value.replace('http://', '').split(':')
		ip = value[0]
		port = value[1]
		result = proxy_db_session.query(Proxys).filter(Proxys.ip == ip).filter(Proxys.port == port).first()
		return result
	value = proxy_dict.get('https')
	if value:
		value = value.replace('https://', '').split(':')
		ip = value[0]
		port = value[1]
		result = proxy_db_session.query(Proxys).filter(Proxys.ip == ip).filter(Proxys.port == port).first()
		return result
	return None

@db_commit_decorator
def del_proxy_by_id(proxy_id):
	proxy = proxy_db_session.query(Proxys).filter(Proxys.id == proxy_id).one()
	if proxy:
		proxy_db_session.delete(proxy)
		proxy_db_session.commit()

# 有相对模式和绝对模式
@db_commit_decorator
def set_proxy_score(proxy_dict, new_score, relative = True):
	max_proxy_cnt = 20
	proxy = get_proxy_by_dict(proxy_dict)
	if proxy:
		if relative:
			proxy.score = proxy.score + new_score
		else:
			proxy.score = new_score
		if proxy.score <= 0:
			del_proxy_by_id(proxy.id)
			return True
		proxy_db_session.commit()
		return True
	return False

		

