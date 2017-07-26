# coding:utf-8
import time
from logger.log import crawler
from tasks.workers import app
from page_parse.user import public
from page_get.basic import get_page
from db.wb_data import insert_weibo_datas
from db.seed_ids import get_home_ids
from config.conf import get_max_home_page
from page_parse.home import get_wbdata_fromweb, get_home_wbdata_byajax, get_total_page
# new import for wb_pic
from db.wb_pic import insert_weibo_pics
from db.seed_ids import set_seed_home_crawled

# 只抓取原创微博
home_url = 'http://weibo.com/u/{}?is_ori=1&is_tag=0&profile_ftype=1&page={}'
ajax_url = 'http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={}&pagebar={}&is_ori=1&id={}{}&page={}' \
           '&pre_page={}&__rnd={}'


@app.task(ignore_result=True)
def crawl_ajax_page(url):
    """
    返回值主要供第一次本地调用使用（获取总页数），网络调用忽略返回值
    :param url: 
    :return: 
    """
    ajax_html = get_page(url, user_verify=False)
    ajax_wbdatas, ajax_wbpics = get_home_wbdata_byajax(ajax_html)
    if not ajax_wbdatas:
        return ''

    insert_weibo_datas(ajax_wbdatas)

    if ajax_wbpics:
        insert_weibo_pics(ajax_wbpics)
    
    return ajax_html


@app.task(ignore_result=True)
def crawl_weibo_datas(uid):
    limit = get_max_home_page()
    cur_page = 1

    # 自定义最大爬取的页数
    max_page = 10
    # end

    while cur_page <= limit:

        # 有些微博账号的照片多达两三千张，如果全部爬取比较浪费时间，这里先简单粗暴地根据当前微博的页数
        # 进行限制。经过调查发现10页左右应该是比较理想的数字，电脑版微博一页有45条微博，那么一个账户就是
        # 450条微博。
        if cur_page > max_page:
            break
        # end

        url = home_url.format(uid, cur_page)
        html = get_page(url)

        domain = public.get_userdomain(html)
        # 只爬取微博个人用户的相片，如果是非个人用户（如政府，组织等）不爬取。
        if domain not in ['103505', '100306', '100505', '']:
            set_seed_home_crawled(uid, 2)
            return
        # end

        weibo_datas, weibo_pics = get_wbdata_fromweb(html)

        if not weibo_datas:
            crawler.warning('用户id为{}的用户主页微博数据未采集成功，请检查原因'.format(uid))
            return

        insert_weibo_datas(weibo_datas)

        # 如果非空，则将weibo_pics插入数据库中
        if weibo_pics:
            insert_weibo_pics(weibo_pics)
        # end

        cur_time = int(time.time()*1000)
        ajax_url_0 = ajax_url.format(domain, 0, domain, uid, cur_page, cur_page, cur_time)
        ajax_url_1 = ajax_url.format(domain, 1, domain, uid, cur_page, cur_page, cur_time+100)

        if cur_page == 1:
            total_page = get_total_page(crawl_ajax_page(ajax_url_1))

        if total_page < limit:
            limit = total_page

        cur_page += 1
        app.send_task('tasks.home.crawl_ajax_page', args=(ajax_url_0,), queue='ajax_home_crawler',
                      routing_key='ajax_home_info')

        app.send_task('tasks.home.crawl_ajax_page', args=(ajax_url_1,), queue='ajax_home_crawler',
                      routing_key='ajax_home_info')
        

    # 在遍历完所有页数之后，将flag置位。放在这里表示所有页面都遍历过，不保证遍历成功后置位。可能以后还要优化，即在
    # 某个回调函数中使用它。
    set_seed_home_crawled(uid)
    # end

@app.task
def excute_home_task():
    # 这里的策略由自己指定，可以基于已有用户做主页抓取，也可以指定一些用户,我这里直接选的种子数据库中的uid
    id_objs = get_home_ids()
    for id_obj in id_objs:
        app.send_task('tasks.home.crawl_weibo_datas', args=(id_obj.uid,), queue='home_crawler',
                      routing_key='home_info')