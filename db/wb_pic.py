# coding:utf-8
from sqlalchemy import text
from db.basic_db import db_session
from db.models import WeiboPic
from decorators.decorator import db_commit_decorator

# to judge that is there have a record in database.
def get_pic_by_url(url, url_hash):
	r = db_session.query(WeiboPic).filter(WeiboPic.url_hash == url_hash).first()
	if r:
		if r.url == url:
			return True
	return False

@db_commit_decorator
def insert_weibo_pics(weibo_pics):
    for pic in weibo_pics:
    	r = get_pic_by_url(pic.pic_url, pic.url_hash)
    	if not r:
        	db_session.add(pic)
    db_session.commit()


# select pic_url from db limit number
# [(uid, url), ...]
def get_pic_url_by_limit(num):
	# r = db_session.query(WeiboPic.pic_url).filter(text('dl_flag=0')).limit(num)
	r = db_session.query(WeiboPic.uid, WeiboPic.pic_url).filter(WeiboPic.dl_flag == 0).limit(num).all()
	return r