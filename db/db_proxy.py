# coding:utf-8
from db.basic_db import proxy_db_session
from db.models import Proxys
from decorators.decorator import db_commit_decorator
from sqlalchemy import func
from random import randint

def count_proxy():
	return (proxy_db_session.query(func.count(Proxys.id)).first())[0]

# 正常情况下如果count>num，返回num条，否则返回count条，其他情况返回空数组
# 在这里只寻找https代理
def fetch_proxy(status = 1, num = 1):
	if num <= 0:
		return []
	count = count_proxy()
	if status == 1:
		if count >= num:
			return proxy_db_session.query(Proxys).filter(Proxys.protocol != 0).order_by(Proxys.score, Proxys.speed).limit(num).all()
		elif count > 0:
			return proxy_db_session.query(Proxys).filter(Proxys.protocol != 0).order_by(Proxys.score, Proxys.speed).limit(count).all()
		else:
			return []
	elif status == 0:
		if count >= num:
			return proxy_db_session.query(Proxys).filter(Proxys.protocol != 1).order_by(Proxys.score, Proxys.speed).limit(num).all()
		elif count > 0:
			return proxy_db_session.query(Proxys).filter(Proxys.protocol != 1).order_by(Proxys.score, Proxys.speed).limit(count).all()
		else:
			return []

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

def del_proxy_by_id(proxy_id):
	proxy = proxy_db_session.query(Proxys).filter(Proxys.id == proxy_id).one()
	if proxy:
		proxy.delete()

# 有相对模式和绝对模式
@db_commit_decorator
def set_proxy_score(proxy_dict, new_score, relative = True):
	proxy = get_proxy_by_dict(proxy_dict)
	if proxy:
		if relative:
			proxy.score = proxy.score + new_score
		else:
			proxy.score = new_score
		if proxy.score <= 0:
			del_proxy_by_id(proxy.id)
			return None
		proxy_db_session.commit()

# 设置一个标志位，指定当protocol=2时，是将其作为http代理还是https代理，默认为http代理
def parse_a_proxy_to_dict(proxy, reg_flag=1):
	if proxy:
		if proxy.protocol == 0 or (proxy.protocol == 2 and reg_flag == 0):
			addr = 'http://' + proxy.ip + ':' + str(proxy.port)
			prot = 'http'
			return {prot: addr}
		elif proxy.protocol == 1 or (proxy.protocol == 2 and reg_flag == 1):
			addr = 'https://' + proxy.ip + ':' + str(proxy.port)
			prot = 'https'
			return {prot: addr}	
		return {}
		
def get_a_random_proxy():
	http_proxys = fetch_proxy(0, 40)
	http_count = len(http_proxys)
	if http_count == 0:
		return {}
	http_index = randint(0, http_count-1)
	http_dict = parse_a_proxy_to_dict(http_proxys[http_index], 0)

	https_proxys = fetch_proxy(1, 40)
	https_count = len(https_proxys)
	if https_count == 0:
		return {}
	https_index = randint(0, https_count-1)
	https_dict = parse_a_proxy_to_dict(https_proxys[https_index], 1)
	return dict(http_dict, **https_dict)
		

