# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys

# test code
if __name__ == '__main__':
	r = proxy_db_session.query(Proxys).filter(Proxys.id== 1).first()
	print(r.createtime)
# end
