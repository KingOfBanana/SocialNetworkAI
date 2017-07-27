# -*-coding:utf-8 -*-
import re
import json
from bs4 import BeautifulSoup
from logger.log import parser
from page_get import status
# from db.models import WeiboData
from db.models import WeiboData, WeiboPic
from decorators.decorator import parse_decorator

# 为了避免确实没有发过带图微博和解析错误的混淆，要把空值主动返回和解析错误返回的空值区分开来

# 如果解析错误则返回None
@parse_decorator(5)
def get_pic_info_from_script(html):

    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all('script')
    pattern = re.compile(r'FM.view\((.*)\)')

    cont = ''
    for script in scripts:
        m = pattern.search(script.string)
        if m and 'photo_module' in script.string:
            all_info = m.group(1)
            cont += json.loads(all_info).get('html', '')
    return cont

# 即使返回('', '', '')，也是非空
@parse_decorator(5)
def get_pic_info_by_re(re_str, src_str):
    uid = mid = pid = ''
    result = re.match(r'uid=(.*)&mid=(.*)&pid=(.*)&', src_str)
    if result:
        uid = result.group(1)
        mid = result.group(2)
        pid = result.group(3)
    return uid, mid, pid

@parse_decorator(5)
def get_next_ajax_url(html):
    if html is None:
        return None
    if not html:
        return list()
    soup = BeautifulSoup(html, "html.parser")

    ajax_url = ''
    ajax_url_class = soup.find(attrs={'class': 'WB_cardwrap S_bg2'})
    if ajax_url_class:
        ajax_url = ajax_url_class.get('action-data')

    return ajax_url

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

def get_wbdata_fromweb(html):
    """
    从主页获取具体的微博数据
    :param html: 
    :return: 
    """
    cont = get_pic_info_from_script(html)
    return get_pic_list(cont), get_next_ajax_url(cont)

# json.load有时候会出现意外的exception，又因为接收的是两个返回值，不好加装饰器，
# 所以直接用try catch的形式。
def get_pic_data_byajax(html):
    try:
        cont = json.loads(html, encoding='utf-8').get('data', '')
    except Exception as e:
        return None, None
    return get_pic_list(cont), get_next_ajax_url(cont)