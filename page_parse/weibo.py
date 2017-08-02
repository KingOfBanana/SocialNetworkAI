# -*-coding:utf-8 -*-
import re
import json
from bs4 import BeautifulSoup
from logger.log import parser
from page_get import status
# from db.models import WeiboData
from db.models import WeiboData, WeiboPic
from decorators.decorator import parse_decorator


@parse_decorator(5)
def get_pic_list(html):
    """
    get the list of weibo info
    :param html: 
    :return: 
    """
    if html is None:
        return None

    if not html:
        return list()
    
    weibo_pics = []
    soup = BeautifulSoup(html, "html.parser")
    photo_list = soup.find_all(attrs={'class': 'ph_ar_box'})

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
            
    return weibo_pics

@parse_decorator(3)
def parse_json_to_dict(html):
    cont = json.loads(html, encoding='utf-8')
    return cont

# 如果在某一页中并没有收获到图片，也不应该判断为错误（None）
@parse_decorator(5)
def parse_dict_to_wb_list(wb_dict):
    weibo_pic_list = []
    cards = wb_dict['cards']
    if cards:
        for card in cards:
            if card['mblog']:
                one_wb_pic_list = mblog_to_db_handler(card['mblog'])
                if one_wb_pic_list:
                    weibo_pic_list.extend(one_wb_pic_list)
    return weibo_pic_list

# [] - 该用户的微博已经被遍历到底
# [data] - 正常解析
# 其他各种异常情况
def get_weibo_list(html):
    cont = parse_json_to_dict(html)
    check_bt_flag = check_no_bottom(cont)
    if check_bt_flag:
        return parse_dict_to_wb_list(cont)
    elif check_bt_flag == False:
        return False
    else:
        return None

@parse_decorator(2)
def mblog_to_db_handler(mblog_dict):
    pics = mblog_dict['pics']
    mid = mblog_dict['mid']
    uid = mblog_dict['user']['id']
    wb_pic_list = list()
    if pics:
        for pic in pics:
            wb_pic = WeiboPic()
            wb_pic.uid = uid
            wb_pic.weibo_id = mid
            wb_pic.url_hash = pic['pid']

            wb_pic.pic_url = pic['url']
            wb_pic.pic_url = wb_pic.pic_url.replace('https:', '')
            wb_pic.pic_url = wb_pic.pic_url.replace('/orj360/', '/thumb150/')
            
            wb_pic.dl_flag = 0
            wb_pic.judge_flag = 0
            wb_pic_list.append(wb_pic)
    return wb_pic_list


# 返回值为True代表未到达底部，否则已经是底部了
# 返回False有可能是两种情况，一是确实到底部，二是解析错误，返回false。
@parse_decorator(5)
def check_no_bottom(wb_dict):
    # if len(wb_dict['cards']) == 1 and wb_dict['cards'][0]['name'] == '暂无微博':
    #     return False
    # elif wb_dict['cardlistInfo']['page'] or len(wb_dict['cards']) >= 1:
    #     return True
    # else:
    #     return None
    if 'cards' in wb_dict:
        if len(wb_dict['cards']) == 1:
            if 'mblog' in wb_dict['cards'][0]:
                return True
            elif 'name' in wb_dict['cards'][0]:
                if wb_dict['cards'][0]['name'] == '暂无微博':
                    return False
        elif len(wb_dict['cards']) > 1:
            return True
        else:
            return None
    else:
        return None



