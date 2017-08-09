# -*-coding:utf-8 -*-
from page_get.basic import get_page
from decorators.decorator import parse_decorator

def get_fans_list_return(uid, page):
	fans_wb_temp_url = 'https://m.weibo.cn/api/container/getIndex?containerid={}_-_followers_-_{}&luicode={}&lfid={}&featurecode={}&type=uid&value={}&page={}'
	
	containerid = '231051'
	luicode = '10000011'
	lfid = '100505' + str(uid)
	featurecode = '20000320'
	value = str(uid)

	url = fans_wb_temp_url.format(containerid, uid, luicode, lfid, featurecode, value, page)
	html = get_page(url, user_verify=False, need_login=False)
	return url, html
	

