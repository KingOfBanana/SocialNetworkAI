# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys
from db.redis_db import Proxys_Redis
from db.db_proxy import del_proxy_by_id, insert_proxy
from page_parse.proxy import get_proxy_to_db, get_a_random_proxy
from db.seed_ids import get_ids_by_home_flag_random, get_home_ids

json_return = '{"ERRORCODE":"0","RESULT":[{"port":"43617","ip":"222.85.5.118"},{"port":"43569","ip":"180.122.20.108"},{"port":"20443","ip":"221.230.254.73"}]}'

# test code
if __name__ == '__main__':
	# url = 'http://127.0.0.1/phptest/xundaili.php'
	# get_proxy_to_db()
	# print(get_a_random_proxy())
	seeds = get_ids_by_home_flag_random(0, 5)
	old_seeds = get_home_ids(0, 5)
	if seeds:
		for seed in seeds:
			print('new: ', seed.uid)
	if old_seeds:
		for old_seed in old_seeds:
			print('old: ',old_seed.uid)	

# end