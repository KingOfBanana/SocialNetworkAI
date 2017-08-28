# coding:utf-8
import time
from logger.log import crawler
from tasks.workers import app
from page_parse.user import public
from page_get.basic import get_page
from db.seed_ids import get_home_ids, get_ids_by_home_flag_random
from config.conf import get_max_home_page
from page_parse.weibo import get_weibo_list
# new import for wb_pic
from db.wb_pic import insert_weibo_pics
from db.seed_ids import set_seed_home_crawled

from db.db_proxy import count_proxy
from page_parse.proxy import get_a_random_proxy
from page_parse.proxy import proxy_handler, get_proxy_to_db, proxy_init

from random import randint
from utils.random_gen import random_event_occur

import requests
from headers import headers

ori_pic_temp_url = 'https://m.weibo.cn/api/container/getSecond?containerid=107803{}_-_photoall&page={}&count=24&luicode=10000011&lfid=107803_{}&featurecode=20000320'

# @app.task(ignore_result=True)
def crawl_weibo_pic(uid):
    cur_page = 1

    pic_count = 0
    max_pic_count = 150

    max_retry_cnt = 2
    cur_retry_cnt = 0

    direct_get_sleep_time = 30

    page = cur_page

    # 只要db中没有proxy，就认为当前进入了一个暂时无代理而需要直接连接的状况，sleep的时间就应该相应的拉长
    proxy = get_a_random_proxy()
    if proxy == {}:
        direct_get_sleep_time = 60
    elif random_event_occur():
        proxy = {}
    print(proxy)
    # end

    # test for getting empty proxy
    if proxy == {}:
        time.sleep(randint(0, direct_get_sleep_time))
    # end

    url = ori_pic_temp_url.format(uid, page, uid)
    cookies = dict(M_WEIBOCN_PARAMS='luicode%3D10000011%26lfid%3D107803_1680102074%26featurecode%3D20000320%26oid%3D4145674154822794%26fid%3D1078031680102074_-_photoall%26uicode%3D10000012')
    # html = get_page(url, user_verify=False, need_login=False, proxys=proxy, cookies=cookies)
    html = requests.get(url, headers=headers, timeout=200, proxies=proxy, cookies=cookies)
    print(html.text)

# @app.task
def excute_weibo_pic_task():
    id_objs = get_ids_by_home_flag_random(0, 1)
    proxy_init()
    for id_obj in id_objs:
        # app.send_task('tasks.weibo.crawl_weibo', args=(id_obj.uid,), queue='weibo_crawler',
        #               routing_key='weibo_info')
        crawl_weibo_pic(id_obj.uid)