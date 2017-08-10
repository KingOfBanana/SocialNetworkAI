# coding:utf-8
# from db.redis_db import Proxys
from db.basic_db import proxy_db_session
from db.models import Proxys
from db.redis_db import Proxys_Redis
from page_parse.proxy import get_proxy_to_db
from page_get.basic import get_page

# url = 'http://dev.kuaidaili.com/api/getproxy/?orderid=980236660103830&num=50&area=%E4%B8%AD%E5%9B%BD&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=2&method=1&an_an=1&an_ha=1&sep=1'
# test code
if __name__ == '__main__':
	get_proxy_to_db()
# end