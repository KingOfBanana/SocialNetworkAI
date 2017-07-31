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
from db.db_proxy import get_proxy, set_proxy_score

# 因为pic_url里需要domain，所以得先从不需要domain只需要uid的home_url里面开始爬，获取domain
# home_url = 'http://weibo.com/u/{}?is_ori=1&is_tag=0&profile_ftype=1&page={}'
# pic_url = 'http://weibo.com/p/{}/photos?from={}&mod=TAB#place'
# ajax_url = 'http://weibo.com/p/aj/album/loading?ajwvr=6&page_id={}&page={}&ajax_call={}&__rnd={}'

ori_wb_temp_url = 'http://m.weibo.cn/api/container/getIndex?containerid={}_-_WEIBO_SECOND_PROFILE_WEIBO_ORI&luicode={}&lfid={}&featurecode={}&type=uid&value={}&page_type={}&page={}'

@app.task(ignore_result=True)
def crawl_weibo(uid, proxys={}):
    limit = get_max_home_page()
    cur_page = 1

    # 自定义最大爬取的页数
    max_page = 70
    # end

    containerid = '230413' + uid
    luicode = '10000011'
    lfid = '230283' + uid
    featurecode = '20000180'
    value = uid
    page_type = '03'
    page = cur_page

    url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)
    html = get_page(url, user_verify=False, need_login=False, proxys=proxys)
    weibo_pics = get_weibo_list(html)
    if weibo_pics:
        insert_weibo_pics(weibo_pics)
    cur_page += 1

    # html为空也有可能是其他原因，但是代理问题应该是大概率，因此对代理进行扣分。
    if html == '':
        crawler.warning('用户id为{}的相册采集出错'.format(uid))
        set_seed_home_crawled(uid, 3)

        if set_proxy_score(proxys, -1) == None:
            proxys = get_proxy()
            if proxys:
                proxy = proxys[0]
        return
    # end
    
    while cur_page <= limit:
        if cur_page > max_page:
            return
        page = cur_page
        url = ori_wb_temp_url.format(containerid, luicode, lfid, featurecode, value, page_type, page)

        weibo_pics = get_weibo_list(html)
        if weibo_pics:
            insert_weibo_pics(weibo_pics)
        cur_page += 1

    crawler.warning('用户id为{}的相册采集完成'.format(uid))
    set_seed_home_crawled(uid, 4)
    set_proxy_score(proxys, 1)
    return

@app.task
def excute_weibo_task():
    id_objs = get_home_ids(0, 1000)

    proxys = get_proxy()
    if proxys:
        proxy = proxys[0]

    for id_obj in id_objs:
        app.send_task('tasks.weibo.crawl_weibo', args=(id_obj.uid,), queue='weibo_crawler',
                      routing_key='weibo_info')
        # crawl_weibo(id_obj.uid, proxys=proxy)


# @app.task(ignore_result=True)
# def crawl_weibo_pics(uid):
#     limit = get_max_home_page()
#     cur_page = 1

#     # 自定义最大爬取的页数
#     max_page = 20
#     # end

#     url = home_url.format(uid, cur_page)
#     html = get_page(url)
#     domain = public.get_userdomain(html)
    
#     # 只爬取微博个人用户的相片，如果是非个人用户（如政府，组织等）不爬取。
#     if domain not in ['103505', '100306', '100505', '']:
#         set_seed_home_crawled(uid, 2)
#         return
#     # end

#     domain_uid = domain + uid
#     page_domain = 'page_' + domain
#     url = pic_url.format(domain_uid, page_domain)

#     html = get_page(url)

#     weibo_pics, next_ajax_url = get_wbdata_fromweb(html)

#     if weibo_pics is None or next_ajax_url is None:
#         crawler.warning('用户id为{}的用户相册未采集成功，请检查原因'.format(uid))
#         set_seed_home_crawled(uid, 3)
#         return

#     if not weibo_pics:
#         crawler.warning('用户id为{}的用户相册未采集成功，可能是因为TA没有发过带图微博'.format(uid))
#         set_seed_home_crawled(uid, 5)
#         return

#     insert_weibo_pics(weibo_pics)

#     if not next_ajax_url:
#         crawler.warning('用户id为{}的相册采集完成'.format(uid))
#         set_seed_home_crawled(uid, 4)
#         return
    
#     cur_page += 1

#     while cur_page <= limit:

#         # 有些微博账号的照片多达两三千张，如果全部爬取比较浪费时间，这里先简单粗暴地根据当前微博的页数
#         # 进行限制。经过调查发现10页左右应该是比较理想的数字。
#         if cur_page > max_page:
#             break
#         # ebd

#         cur_time = int(time.time()*1000)
#         ajax_call = 1
#         page_id = domain_uid
#         url = ajax_url.format(page_id, cur_page, ajax_call, cur_time) + '&' + next_ajax_url
#         html = get_page(url, user_verify=False)

#         weibo_pics, next_ajax_url = get_pic_data_byajax(html)
        
#         if weibo_pics is None or next_ajax_url is None:
#             crawler.warning('用户id为{}的用户相册未采集成功，请检查原因'.format(uid))
#             set_seed_home_crawled(uid, 3)
#             return

#         if not weibo_pics:
#             crawler.warning('用户id为{}的用户相册未采集成功，请检查原因'.format(uid))
#             set_seed_home_crawled(uid, 3)
#             return
        
#         insert_weibo_pics(weibo_pics)
        
#         if not next_ajax_url:
#             crawler.warning('用户id为{}的相册采集完成'.format(uid))
#             set_seed_home_crawled(uid, 4)
#             return

#         cur_page += 1
        
#     # 在完成规定的最大爬取页数后主动退出，将标志位置位为4
#     set_seed_home_crawled(uid, 4)
#     return
#     # end


# @app.task
# def excute_pic_task():
#     # 这里的策略由自己指定，可以基于已有用户做主页抓取，也可以指定一些用户,我这里直接选的种子数据库中的uid
#     id_objs = get_home_ids(0)
#     for id_obj in id_objs:
#         app.send_task('tasks.pic.crawl_weibo_pics', args=(id_obj.uid,), queue='pic_crawler',
#                       routing_key='pic_info')
#         # crawl_weibo_pics(id_obj.uid)




