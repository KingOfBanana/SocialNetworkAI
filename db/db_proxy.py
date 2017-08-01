# coding:utf-8
from db.basic_db import proxy_db_session
from db.models import Proxys
from decorators.decorator import db_commit_decorator
from sqlalchemy import func
from random import randint

def count_proxy():
	return (proxy_db_session.query(func.count(Proxys.id)).first())[0]

def fetch_proxy(num = 1):
	count = count_proxy()
	if count >= num:
		return proxy_db_session.query(Proxys).order_by(Proxys.speed).limit(num).all()
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
		if proxy.score == 0:
			del_proxy_by_id(proxy.id)
			return None
		proxy_db_session.commit()

# def change_proxy_score(proxy_dict, delta):
# 	score = get_proxy_score(proxy_dict, )
# 	new_score = score + delta

# 获取一定数量的代理，返回的是requests proxy可以直接用的字典型数组
def get_proxy(num = 1):
	result = []
	proxys = fetch_proxy(num)
	if proxys:
		for proxy in proxys:
			if proxy.protocol == 0 or proxy.protocol == 2:
				addr = 'http:' + proxy.ip + ':' + str(proxy.port)
				prot = 'http:'
			elif proxy.protocol == 1:
				addr = 'https:' + proxy.ip + ':' + str(proxy.port)
				prot = 'https:'
			result.append({prot: addr})
	return result

def get_a_random_proxy():
	proxys = get_proxy()
	if proxys:
		return proxys[0]
	else:
		return {}

