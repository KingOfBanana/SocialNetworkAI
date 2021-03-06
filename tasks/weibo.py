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

ori_wb_temp_url = 'https://m.weibo.cn/api/container/getIndex?containerid={}_-_WEIBO_SECOND_PROFILE_WEIBO_ORI&luicode={}&lfid={}&featurecode={}&type=uid&value={}&page_type={}&page={}'

# @app.task(ignore_result=True)
def crawl_weibo(uid):
    debug_mode = 1

    limit = get_max_home_page()
    cur_page = 1

    pic_count = 0
    max_pic_count = 150

    max_retry_cnt = 2
    cur_retry_cnt = 0

    direct_get_sleep_time = 30

    containerid = '230413' + uid
    luicode = '10000011'
    lfid = '230283' + uid
    featurecode = '20000180'
    value = uid
    page_type = '03'
    page = cur_page

    # 只要db中没有proxy，就认为当前进入了一个暂时无代理而需要直接连接的状况，sleep的时间就应该相应的拉长
    proxy = get_a_random_proxy()
    if proxy == {}:
        direct_get_sleep_time = 60
    elif random_event_occur():
        proxy = {}
    print(proxy)
    # end

    if debug_mode == 1:
        direct_get_sleep_time = 1
    # test for getting empty proxy
    if proxy == {}:
        # crawler.warning('empty proxy!')
        # time.sleep(3)
        # proxy = get_a_random_proxy()
        # proxy_cnt = count_proxy()
        # crawler.warning('new proxy:{}, proxy count:{}'.format(proxy, proxy_cnt))
        # return
        time.sleep(randint(0, direct_get_sleep_time))
    # end

    url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)
    html = get_page(url, user_verify=False, need_login=False, proxys=proxy)

    # html为空也有可能是其他原因，但是代理问题应该是大概率，因此对代理进行扣分。
    # 如果重试还是返回空html，那么两个proxy均不扣分，记录uid异常后直接return，如果返回非空但无效的html，则在后面流程进行扣分
    if html == '':
        if cur_retry_cnt < max_retry_cnt:
            cur_retry_cnt = cur_retry_cnt + 1
            proxy_handler(proxy, -1)
            proxy = get_a_random_proxy()

            if proxy == {}:
                time.sleep(randint(0, direct_get_sleep_time))

            html = get_page(url, user_verify=False, need_login=False, proxys=proxy)
            if html == '':
                proxy_handler(proxy, -1)
                return
        else:
            proxy_handler(proxy, -1)
            return
    # end

    weibo_pics = get_weibo_list(html)

    if weibo_pics == '':
        crawler.warning('请求过于频繁')
        if proxy == {}:
            time.sleep(randint(0, direct_get_sleep_time))
        proxy_handler(proxy, -1)
        return

    if weibo_pics == None:
        proxy_handler(proxy, -1)
        return
    elif weibo_pics == False:
        finish_uid_handler(uid, proxy)
        return
    elif weibo_pics:
        insert_weibo_pics(weibo_pics)

    pic_count = pic_count + len(weibo_pics)

    cur_page += 1

    while cur_page <= limit and pic_count < max_pic_count:
        
        page = cur_page
        url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)
        html = get_page(url, user_verify=False, need_login=False, proxys=proxy)

        # html为空也有可能是其他原因，但是代理问题应该是大概率，因此对代理进行扣分。
        if html == '':
            if cur_retry_cnt < max_retry_cnt:
                cur_retry_cnt = cur_retry_cnt + 1
                proxy_handler(proxy, -1)
                proxy = get_a_random_proxy()

                if proxy == {}:
                    time.sleep(randint(0, direct_get_sleep_time))
                
                html = get_page(url, user_verify=False, need_login=False, proxys=proxy)
                if html == '':
                    exception_uid_handler(uid, 6, proxy)
                    return
            else:
                exception_uid_handler(uid, 3, proxy)
                return
        # end

        weibo_pics = get_weibo_list(html)

        # 如果通过当前代理所获取到的页面是被封锁页面，则将当前代理降分并直接return
        if weibo_pics == '':
            crawler.warning('请求过于频繁')
            if proxy == {}:
                time.sleep(randint(0, direct_get_sleep_time))
            proxy_handler(proxy, -1)
            return

        if weibo_pics == None:
            exception_uid_handler(uid, 4, proxy, html)
            return
        elif weibo_pics == False:
            finish_uid_handler(uid, proxy)
            return
        elif weibo_pics:
            insert_weibo_pics(weibo_pics)
        
        pic_count = pic_count + len(weibo_pics)

        cur_page += 1

    finish_uid_handler(uid, proxy)
    return

# @app.task
def excute_weibo_task():
    id_objs = get_ids_by_home_flag_random(0, 2000)
    proxy_init()
    for id_obj in id_objs:
        # app.send_task('tasks.weibo.crawl_weibo', args=(id_obj.uid,), queue='weibo_crawler',
        #               routing_key='weibo_info')
        crawl_weibo(id_obj.uid)

def finish_uid_handler(uid, proxy):
    crawler.warning('用户id为{}的相册采集完成'.format(uid))
    set_seed_home_crawled(uid, 4)
    proxy_handler(proxy, 1)

def exception_uid_handler(uid, err_code, proxy ={}, html=''):
    crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，状态码{}'.format(uid, html, err_code))
    # set_seed_home_crawled(uid, 3)
    if proxy:
        proxy_handler(proxy, -1)

