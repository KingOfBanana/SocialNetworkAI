# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys
from db.redis_db import Proxys_Redis
from db.db_proxy import count_proxy, fetch_proxy, get_proxy_by_dict, set_proxy_score, del_proxy_by_id, get_a_random_proxy

# 获取一定数量的代理，如果这时候还未初始化，则先从sql中获取一定数量的代理放入redis中
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

# test code
if __name__ == '__main__':
	print(get_a_random_proxy())
# end