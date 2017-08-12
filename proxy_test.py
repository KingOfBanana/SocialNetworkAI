# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys
from db.redis_db import Proxys_Redis
from page_parse.proxy import get_proxy_to_db
from page_get.basic import get_page
from utils.random_gen import random_event_occur

# test code
if __name__ == '__main__':
	get_proxy_to_db()
	# get_proxy_to_db()
# end