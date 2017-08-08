import json
from decorators.decorator import parse_decorator
from page_get.basic import get_page
from db.models import Proxys
from db.db_proxy import del_proxy_by_id, insert_proxy, fetch_proxy, set_proxy_score, count_proxy
from random import randint

@parse_decorator(3)
def parse_json_to_dict(html):
    cont = json.loads(html, encoding='utf-8')
    return cont

@parse_decorator(3)
def get_proxy_to_db():
	url = 'http://www.xdaili.cn/ipagent/greatRecharge/getGreatIp?spiderId=6b93c4863a7f4bc986b8046a169be574&orderno=YZ201783933405gg7L&returnType=2&count=20'
	html = get_page(url, user_verify=False, need_login=False)
	proxy_dict = parse_json_to_dict(html)
	proxies = proxy_dict.get('RESULT')
	proxy_list = []
	if proxies:
		for proxy in proxies:
			port = proxy.get('port')
			ip = proxy.get('ip')
			new_proxy = Proxys()
			new_proxy.ip = ip
			new_proxy.port = port
			new_proxy.types = 2
			new_proxy.protocol = 2
			new_proxy.country = '国内'
			new_proxy.area = '讯代理'
			new_proxy.speed = 0.00
			new_proxy.score = 5
			proxy_list.append(new_proxy)
	if proxy_list:
		insert_proxy(proxy_list)
		return True
	else:
		return False

@parse_decorator(3)
def get_mpproxy_to_db():
	url = 'http://proxy.mimvp.com/api/fetch.php?orderid=860170808163932696&num=100&country_group=1&http_type=2&anonymous=3,5&result_fields=1,2&result_format=json'
	html = get_page(url, user_verify=False, need_login=False)
	proxy_dict = parse_json_to_dict(html)
	proxies = proxy_dict.get('result')
	proxy_list = []
	if proxies:
		for proxy in proxies:
			data = proxy.get('ip:port')
			data = data.split(':')
			if data:
				ip = data[0]
				port = data[1]
			else:
				return False
			new_proxy = Proxys()
			new_proxy.ip = ip
			new_proxy.port = port
			new_proxy.types = 2
			new_proxy.protocol = 2
			new_proxy.country = '国内'
			new_proxy.area = '米扑代理'
			new_proxy.speed = 0.00
			new_proxy.score = 5
			proxy_list.append(new_proxy)
	if proxy_list:
		insert_proxy(proxy_list)
		return True
	else:
		return False

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

@parse_decorator(4)
def get_a_random_proxy(num = 50):
	http_proxys = fetch_proxy(0, num)
	http_count = len(http_proxys)
	if http_count == 0:
		return {}
	http_index = randint(0, http_count-1)
	http_dict = parse_a_proxy_to_dict(http_proxys[http_index], 0)

	https_proxys = fetch_proxy(1, num)
	https_count = len(https_proxys)
	if https_count == 0:
		return {}
	https_index = randint(0, https_count-1)
	https_dict = parse_a_proxy_to_dict(https_proxys[https_index], 1)
	return dict(http_dict, **https_dict)
	# return {}

def proxy_handler(proxy_dict, new_score, relative=True):
	if set_proxy_score(proxy_dict, new_score, relative) == True:
		return proxy_init()

def proxy_init():
	max_proxy_cnt = int(5)
	if count_proxy() <= max_proxy_cnt:
		# return get_proxy_to_db()
		return get_mpproxy_to_db()
	else:
		return True

