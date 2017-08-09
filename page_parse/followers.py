# -*-coding:utf-8 -*-
from page_get.basic import get_page
from decorators.decorator import parse_decorator
import json

def get_followers_list_return(uid, page):
	followers_wb_temp_url = 'https://m.weibo.cn/api/container/getIndex?containerid={}_-_followers_-_{}&luicode={}&lfid={}&featurecode={}&type=uid&value={}&page={}'
	
	containerid = '231051'
	luicode = '10000011'
	lfid = '100505' + str(uid)
	featurecode = '20000320'
	value = str(uid)

	url = followers_wb_temp_url.format(containerid, uid, luicode, lfid, featurecode, value, page)
	html = get_page(url, user_verify=False, need_login=False)
	return html

@parse_decorator(3)
def parse_json_to_dict(html):
    cont = json.loads(html, encoding='utf-8')
    return cont

# 如果在某一页中并没有收获到图片，也不应该判断为错误（None）
@parse_decorator(5)
def parse_dict_to_followers_list(wb_dict):

    weibo_pic_list = []
    cards = wb_dict['cards']
    if cards:
        for card in cards:
        	if 'title' in card:
        	# if card['title'] == '他的全部关注':
        		return 'yes!'
            # if card['title'] == '他的全部关注' or card['title'] == '她的全部关注':
            	
                # one_wb_pic_list = mblog_to_db_handler(card['mblog'])
                # if one_wb_pic_list:
                #     weibo_pic_list.extend(one_wb_pic_list)
    # return weibo_pic_list
    return 'no!'

def get_followers(uid):
	page = 1
	html = get_followers_list_return(uid, page)
	json_dict = parse_json_to_dict(html)
	follower_list = parse_dict_to_followers_list(json_dict)
	return follower_list


