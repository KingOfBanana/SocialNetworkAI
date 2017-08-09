# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys
from db.redis_db import Proxys_Redis
from page_parse.proxy import get_proxy_to_db
from page_parse.followers import get_followers
from time import sleep

# test code
if __name__ == '__main__':
	# get_proxy_to_db()
	print(get_followers(3600364847))
# end