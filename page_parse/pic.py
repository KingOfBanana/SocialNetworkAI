# -*-coding:utf-8 -*-
import re
import json
from bs4 import BeautifulSoup
from logger.log import parser
from page_get import status
# from db.models import WeiboData
from db.models import WeiboData, WeiboPic
from decorators.decorator import parse_decorator
from tools.hashtools import md5Encode

# 如果解析错误则返回''
@parse_decorator(1)
def get_pic_info_from_script(html):

    soup = BeautifulSoup(html, "html.parser")

    # photo_album_list = soup.find_all(attrs={'class': 'photo_album_list'})
    scripts = soup.find_all('script')
    pattern = re.compile(r'FM.view\((.*)\)')

    cont = ''
    for script in scripts:
        m = pattern.search(script.string)
        if m and 'photo_module' in script.string:
            all_info = m.group(1)
            cont += json.loads(all_info).get('html', '')
    
    return cont
# @parse_decorator(1)
# def get_weibo_infos_right(html):
#     """
#     通过网页获取用户主页右边部分（即微博部分）字符串
#     :param html: 
#     :return: 
#     """
#     # soup = BeautifulSoup(html, "html.parser")
#     # scripts = soup.find_all('script')
#     # pattern = re.compile(r'FM.view\((.*)\)')

#     # # 如果字符串'fl_menu'(举报或者帮上头条)这样的关键字出现在script中，则是微博数据区域
#     # cont = ''
#     # for script in scripts:
#     #     m = pattern.search(script.string)
#     #     if m and 'fl_menu' in script.string:
#     #         all_info = m.group(1)
#     #         cont += json.loads(all_info).get('html', '')
#     return html


# @parse_decorator(5)
# def get_weibo_info_detail(each, html):
#     wb_data = WeiboData()


#     user_cont = each.find(attrs={'class': 'face'})
#     user_info = str(user_cont.find('a'))
#     user_pattern = 'id=(\\d+)&amp'
#     m = re.search(user_pattern, user_info)
#     if m:
#         wb_data.uid = m.group(1)
#     else:
#         parser.warning('未提取到用户id,页面源码是{}'.format(html))
#         return None

#     weibo_pattern = 'mid=(\\d+)'
#     m = re.search(weibo_pattern, str(each))
#     if m:
#         wb_data.weibo_id = m.group(1)
#     else:
#         parser.warning('未提取到页面的微博id,页面源码是{}'.format(html))
#         return None

#     time_url = each.find(attrs={'node-type': 'feed_list_item_date'})
#     wb_data.create_time = time_url.get('title', '')
#     wb_data.weibo_url = time_url.get('href', '')
#     if 'weibo.com' not in wb_data.weibo_url:
#         wb_data.weibo_url = 'http://weibo.com{}'.format(wb_data.weibo_url)

#     wb_data.weibo_cont = each.find(attrs={'node-type': 'feed_content'}).find\
#         (attrs={'node-type': 'feed_list_content'}).text.strip()


#     # test for weibo_pic capture
#     # 先判断这条微博是否有带图片，再进行后续的处理
#     try:
#         weibo_pic = []
#         have_pic = 1
#         pic_list = each.find_all(attrs={'action-type': 'fl_pics'})
#     except Exception as e:
#         have_pic = 0

#     if have_pic == 1:
#         for pic in pic_list:
#             wb_pic = WeiboPic()
#             wb_pic.uid = wb_data.uid
#             wb_pic.weibo_id = wb_data.weibo_id
#             wb_pic.pic_url = pic.find('img').get('src')
#             wb_pic.url_hash = md5Encode(wb_pic.pic_url)
#             weibo_pic.append(wb_pic)
#     # end

#     if '展开全文' in str(each):
#         is_all_cont = 0
#     else:
#         is_all_cont = 1

#     try:
#         wb_data.device = each.find(attrs={'class': 'WB_from'}).find(attrs={'action-type': 'app_source'}).text
#     except Exception as e:
#         parser.error('本次解析设备出错，具体是{}'.format(e))
#         wb_data.device = ''

#     try:
#         wb_data.repost_num = int(each.find(attrs={'action-type': 'fl_forward'}).find_all('em')[1].text)
#     except Exception:
#         wb_data.repost_num = 0
#     try:
#         wb_data.comment_num = int(each.find(attrs={'action-type': 'fl_comment'}).find_all('em')[1].text)
#     except Exception:
#         wb_data.comment_num = 0
#     try:
#         wb_data.praise_num = int(each.find(attrs={'action-type': 'fl_like'}).find_all('em')[1].text)
#     except Exception:
#         wb_data.praise_num = 0
    
#     return wb_data, is_all_cont, weibo_pic
@parse_decorator(2)
def get_pic_info_by_re(re_str, src_str):
    result = re.match(r'uid=(.*)&mid=(.*)&pid=(.*)&', src_str)
    if result:
        uid = result.group(1)
        mid = result.group(2)
        pid = result.group(3)
        return uid, mid, pid

def get_next_ajax_url(html):
    if not html:
        return list()
    soup = BeautifulSoup(html, "html.parser")

    ajax_url = ''
    ajax_url_class = soup.find(attrs={'class': 'WB_cardwrap S_bg2'})
    if ajax_url_class:
        ajax_url = ajax_url_class.get('action-data')

    return ajax_url

@parse_decorator(2)
def get_pic_list(html):
    """
    get the list of weibo info
    :param html: 
    :return: 
    """
    if not html:
        return list()
    
    weibo_pics = []
    soup = BeautifulSoup(html, "html.parser")
    photo_list = soup.find_all(attrs={'class': 'ph_ar_box'})
    # if photo_list:
    if len(photo_list) > 0:
        for photo in photo_list:
            pic_data = photo.get('action-data')
            if pic_data:
                uid, mid, pid = get_pic_info_by_re(r'uid=(.*)&mid=(.*)&pid=(.*)&', pic_data)
                wb_pic = WeiboPic()
                wb_pic.uid = uid
                wb_pic.weibo_id = mid
                wb_pic.pic_url = photo.find('img').get('src')
                result = re.match(r'.*(jpg|gif)$', wb_pic.pic_url)
                if not result:
                    break
                wb_pic.pic_url = result.group(0)
                wb_pic.pic_url = wb_pic.pic_url.replace('https:', '')
                wb_pic.pic_url = wb_pic.pic_url.replace('/thumb300/', '/thumb150/')
                wb_pic.url_hash = re.match(r'.*/thumb150/(.*).(jpg|gif)', wb_pic.pic_url).group(1)
                wb_pic.dl_flag = 0
                wb_pic.judge_flag = 0
                weibo_pics.append(wb_pic)
            # wb_pic = WeiboPic()
            # wb_pic.uid = uid
            # wb_pic.pic_url = photo.find('img').get('src')

            # 一个历史遗留问题，之前是采用微博的thumb150进行hash，而相册的略缩图模式(模式3)这里是square，所以只能先换成thumb150再
            # hash以及存入数据库
            # wb_pic.pic_url = wb_pic.pic_url.replace('/square/', '/thumb150/')
            # end

            # wb_pic.url_hash = md5Encode(wb_pic.pic_url)
            # weibo_pics.append(wb_pic)
            # weibo_pic.append(wb_pic)
            # photo.find_all(attrs={'action-type': 'fl_pics'})
            # r = get_weibo_info_detail(data, html)
            # if r is not None:
            #     wb_data = r[0]
            #     if r[1] == 0:
            #         wb_data.weibo_cont = status.get_cont_of_weibo(wb_data.weibo_id)

            #     # 如果pic是非空，则在pic数组中插入
            #     if r[2]:
            #         weibo_pics.extend(r[2])
            #     # end
            #     weibo_datas.append(wb_data)

    return weibo_pics

# def get_max_num(html):
#     """
#     get the total page number
#     :param html: 
#     :return: 
#     """
#     soup = BeautifulSoup(html, "html.parser")
#     href_list = soup.find(attrs={'action-type': 'feed_list_page_morelist'}).find_all('a')
#     return len(href_list)


def get_wbdata_fromweb(html):
    """
    从主页获取具体的微博数据
    :param html: 
    :return: 
    """
    cont = get_pic_info_from_script(html)
    return get_pic_list(cont), get_next_ajax_url(cont)

# def get_home_wbdata_byajax(html):
#     """
#     通过返回的ajax内容获取用户微博信息
#     :param html: 
#     :return: 
#     """
#     cont = json.loads(html, encoding='utf-8').get('data', '')
#     return get_weibo_list(cont)


# def get_total_page(html):
#     """
#     从ajax返回的内容获取用户主页的所有能看到的页数
#     :param html: 
#     :return: 
#     """
#     cont = json.loads(html, encoding='utf-8').get('data', '')
#     if not cont:
#         # todo 返回1或者0还需要验证只有一页的情况
#         return 1
#     return get_max_num(cont)
def get_pic_data_byajax(html):
    if not html:
        return [], []
    cont = json.loads(html, encoding='utf-8').get('data', '')
    return get_pic_list(cont), get_next_ajax_url(cont)