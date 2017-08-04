# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys
from db.redis_db import Proxys_Redis
from db.db_proxy import del_proxy_by_id, insert_proxy, count_proxy
from page_parse.proxy import get_proxy_to_db, get_a_random_proxy, proxy_init
from db.seed_ids import get_ids_by_home_flag_random, get_home_ids
from time import sleep
json_return = '{"ERRORCODE":"0","RESULT":[{"port":"43617","ip":"222.85.5.118"},{"port":"43569","ip":"180.122.20.108"},{"port":"20443","ip":"221.230.254.73"}]}'

# test code
if __name__ == '__main__':
	# url = 'http://127.0.0.1/phptest/xundaili.php'
	# get_proxy_to_db()
	# print(get_a_random_proxy())
	i = 0
	while i < 300:
		proxy = get_a_random_proxy()
		count = count_proxy()
		print('proxy:', proxy)
		print('count:', count)
		sleep(1)
		i = i + 1
	

# end