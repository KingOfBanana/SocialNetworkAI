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

def get_weibo_list(html):
    cont = parse_json_to_dict(html)
    if check_no_bottom(cont):
        return parse_dict_to_wb_list(cont)
    else:
        return []

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
@parse_decorator(3)
def check_no_bottom(wb_dict):
    # if 'cardlistInfo' in wb_dict:
    #     cardlistInfo = wb_dict['cardlistInfo']
    #     if 'page' in cardlistInfo:
    #         page = cardlistInfo['page']
    #         if page == 'null':
    #             return page
    #         else:
    #             return page
    if wb_dict['cardlistInfo']['page']:
        return True
    else:
        return False



