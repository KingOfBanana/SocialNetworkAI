# coding:utf-8
import time
from logger.log import crawler
from tasks.workers import app
from page_parse.user import public
from page_get.basic import get_page
from db.seed_ids import get_home_ids
from config.conf import get_max_home_page
from page_parse.weibo import get_weibo_list
# new import for wb_pic
from db.wb_pic import insert_weibo_pics
from db.seed_ids import set_seed_home_crawled
from db.db_proxy import set_proxy_score, get_a_random_proxy

# import for exception test
# from page_parse.weibo import check_no_bottom, check_no_bottom, parse_json_to_dict
# end
ori_wb_temp_url = 'http://m.weibo.cn/api/container/getIndex?containerid={}_-_WEIBO_SECOND_PROFILE_WEIBO_ORI&luicode={}&lfid={}&featurecode={}&type=uid&value={}&page_type={}&page={}'

# @app.task(ignore_result=True)
def crawl_weibo(uid):

    limit = get_max_home_page()
    cur_page = 1

    pic_count = 0
    max_pic_count = 150

    max_retry_cnt = 2
    cur_retry_cnt = 0

    containerid = '230413' + uid
    luicode = '10000011'
    lfid = '230283' + uid
    featurecode = '20000180'
    value = uid
    page_type = '03'
    page = cur_page

    proxy = get_a_random_proxy()

    # test for proxy
    print(proxy)
    # end
    
    url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)
    html = get_page(url, user_verify=False, need_login=False, proxys=proxy)

    # html为空也有可能是其他原因，但是代理问题应该是大概率，因此对代理进行扣分。
    # 如果重试还是返回空html，那么两个proxy均不扣分，记录uid异常后直接return，如果返回非空但无效的html，则在后面流程进行扣分
    if html == '':
        if cur_retry_cnt < max_retry_cnt:
            proxy = get_a_random_proxy()
            html = get_page(url, user_verify=False, need_login=False, proxys=proxy)
            if html == '':
                crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，状态码{}'.format(uid, html, 5))
                set_seed_home_crawled(uid, 3)
                return
        else:
            exception_uid_handler(uid, 1, proxy)
            return
    # end

    weibo_pics = get_weibo_list(html)

    if weibo_pics == None:
        exception_uid_handler(uid, 2, proxy, html)
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
                proxy = get_a_random_proxy()
                html = get_page(url, user_verify=False, need_login=False, proxys=proxy)
                if html == '':
                    crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，状态码{}'.format(uid, html, 6))
                    set_seed_home_crawled(uid, 3)
                    return
            else:
                exception_uid_handler(uid, 3, proxy)
                return
        # end

        weibo_pics = get_weibo_list(html)

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
    id_objs = get_home_ids(0, 50)

    for id_obj in id_objs:
        # app.send_task('tasks.weibo.crawl_weibo', args=(id_obj.uid,), queue='weibo_crawler',
        #               routing_key='weibo_info')
        crawl_weibo(id_obj.uid)

def finish_uid_handler(uid, proxy):
    crawler.warning('用户id为{}的相册采集完成'.format(uid))
    set_seed_home_crawled(uid, 4)
    set_proxy_score(proxy, 1)

def exception_uid_handler(uid, err_code, proxy ={}, html=''):
    crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，状态码{}'.format(uid, html, err_code))
    set_seed_home_crawled(uid, 3)
    if proxy:
        set_proxy_score(proxy, -1)

