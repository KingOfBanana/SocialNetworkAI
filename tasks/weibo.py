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

ori_wb_temp_url = 'http://m.weibo.cn/api/container/getIndex?containerid={}_-_WEIBO_SECOND_PROFILE_WEIBO_ORI&luicode={}&lfid={}&featurecode={}&type=uid&value={}&page_type={}&page={}'

@app.task(ignore_result=True)
def crawl_weibo(uid):

    limit = get_max_home_page()
    cur_page = 1

    containerid = '230413' + uid
    luicode = '10000011'
    lfid = '230283' + uid
    featurecode = '20000180'
    value = uid
    page_type = '03'
    page = cur_page

    proxy = get_a_random_proxy()
    
    url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)
    html = get_page(url, user_verify=False, need_login=False, proxys=proxy)

    # html为空也有可能是其他原因，但是代理问题应该是大概率，因此对代理进行扣分。
    # 此处可以进行一次延时，重试，不过具体策略还要再研究，以防出现多个页面的多次重试，导致时间的浪费
    if html == '':
        crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，错误码001'.format(uid, html))

        set_seed_home_crawled(uid, 3)
        set_proxy_score(proxy, -1)
        return
    # end

    weibo_pics = get_weibo_list(html)

    if weibo_pics == None:
        crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，错误码002'.format(uid, html))
        set_seed_home_crawled(uid, 3)
        set_proxy_score(proxy, -1)
        return

    if weibo_pics == []:
        crawler.warning('用户id为{}的相册采集完成'.format(uid))
        set_seed_home_crawled(uid, 4)
        set_proxy_score(proxy, 1)
        return

    if weibo_pics:
        insert_weibo_pics(weibo_pics)
    cur_page += 1

    while cur_page <= limit:
        
        page = cur_page
        url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)
        html = get_page(url, user_verify=False, need_login=False, proxys=proxy)

        # html为空也有可能是其他原因，但是代理问题应该是大概率，因此对代理进行扣分。
        if html == '':
            crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，错误码003'.format(uid, html))
            set_seed_home_crawled(uid, 3)
            set_proxy_score(proxy, -1)
            return
        # end

        weibo_pics = get_weibo_list(html)

        if weibo_pics == None:
            crawler.warning('用户id为{}的相册采集出错，这一请求接收到的内容为{}，错误码004'.format(uid, html))
            set_seed_home_crawled(uid, 3)
            set_proxy_score(proxy, -1)
            return

        if weibo_pics == []:
            crawler.warning('用户id为{}的相册采集完成'.format(uid))
            set_seed_home_crawled(uid, 4)
            set_proxy_score(proxy, 1)
            return

        if weibo_pics:
            insert_weibo_pics(weibo_pics)
        cur_page += 1

    crawler.warning('用户id为{}的相册采集完成'.format(uid))
    set_seed_home_crawled(uid, 4)
    set_proxy_score(proxy, 1)
    return

@app.task
def excute_weibo_task():
    id_objs = get_home_ids(0, 500)

    for id_obj in id_objs:
        app.send_task('tasks.weibo.crawl_weibo', args=(id_obj.uid,), queue='weibo_crawler',
                      routing_key='weibo_info')
        # crawl_weibo(id_obj.uid)




