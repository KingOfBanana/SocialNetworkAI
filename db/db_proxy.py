# coding:utf-8
from db.basic_db import proxy_db_session
from db.models import Proxys, ProxySource
from decorators.decorator import db_commit_decorator, proxy_db_commit_decorator
from sqlalchemy import func

@proxy_db_commit_decorator
def insert_proxy(proxies):
	if proxies:
	    for proxy in proxies:
	    	if proxy:
	        	proxy_db_session.add(proxy)
	    proxy_db_session.commit()

@proxy_db_commit_decorator
def count_proxy():
	try:
		cnt = (proxy_db_session.query(func.count(Proxys.id)).first())[0]
		if type(cnt) == int:
			return cnt
		else:
			return 0
	except Exception as e:
		return 0

# 正常情况下如果count>num，返回num条，否则返回count条，其他情况返回空数组
# 在这里只寻找https代理
@proxy_db_commit_decorator
def fetch_proxy(status = 1, num = 1):
	if num <= 0:
		return []
	count = count_proxy()
	result = []
	if status == 1:
		if count >= num:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 0).limit(num).all()
		elif count > 0:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 0).limit(count).all()
	elif status == 0:
		if count >= num:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 1).limit(num).all()
		elif count > 0:
			result = proxy_db_session.query(Proxys).filter(Proxys.protocol != 1).limit(count).all()
	if not result and result != []:
		result = []
	return result
	

@proxy_db_commit_decorator
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

@proxy_db_commit_decorator
def del_proxy_by_id(proxy_id):
	proxy = proxy_db_session.query(Proxys).filter(Proxys.id == proxy_id).one()
	if proxy:
		proxy_db_session.delete(proxy)
		proxy_db_session.commit()

# 有相对模式和绝对模式
@proxy_db_commit_decorator
def set_proxy_score(proxy_dict, new_score, relative=True):
	max_proxy_cnt = 20
	proxy = get_proxy_by_dict(proxy_dict)
	if proxy:
		if relative:
			if new_score < 0 and proxy.last_delta < 0:
				new_score = proxy.last_delta * 2
			proxy.last_delta = new_score
			proxy.score = proxy.score + new_score
		else:
			proxy.score = new_score
		if proxy.score <= 0:
			del_proxy_by_id(proxy.id)
			return True
		proxy_db_session.commit()
		return True
	return False

# 通过指定source的值来获取对应的URL
def get_proxy_source_by_source(source=0):
	proxy_sources = proxy_db_session.query(ProxySource).filter(ProxySource.source == source).filter(ProxySource.status == 1).all()
	return proxy_sources
