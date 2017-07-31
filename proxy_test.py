# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys

# test code
if __name__ == '__main__':
	results = proxy_db_session.query(Proxys).limit(5).all()
	for proxy in results:
		print(proxy.ip)
		print(proxy.area)
# end