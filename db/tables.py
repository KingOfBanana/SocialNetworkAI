# -*-coding:utf-8 -*-
from sqlalchemy import Table, Column, INTEGER, String
from sqlalchemy import DateTime, Numeric, VARCHAR
from db.basic_db import metadata
from db.basic_db import proxy_db_metadata

# login table
login_info = Table("login_info", metadata,
                   Column("id", INTEGER, primary_key=True, autoincrement=True),
                   Column("name", String(100), unique=True),
                   Column("password", String(200)),
                   Column("enable", INTEGER, default=1, server_default='1'),
                   )

# weibo user info
wbuser = Table("wbuser", metadata,
               Column("id", INTEGER, primary_key=True, autoincrement=True),
               Column("uid", String(20), unique=True),
               Column("name", String(200), default='', server_default=''),
               Column("gender", INTEGER, default=0, server_default='0'),
               Column("birthday", String(200), default='', server_default=''),
               Column("location", String(100), default='', server_default=''),
               Column("description", String(500), default='', server_default=''),
               Column("register_time", String(200), default='', server_default=''),
               Column("verify_type", INTEGER, default=0, server_default='0'),
               Column("verify_info", String(2500), default='', server_default=''),
               Column("follows_num", INTEGER, default=0, server_default='0'),
               Column("fans_num", INTEGER, default=0, server_default='0'),
               Column("wb_num", INTEGER, default=0, server_default='0'),
               Column("level", INTEGER, default=0, server_default='0'),
               Column("tags", String(500), default='', server_default=''),
               Column("work_info", String(500), default='', server_default=''),
               Column("contact_info", String(300), default='', server_default=''),
               Column("education_info", String(300), default='', server_default=''),
               Column("head_img", String(500), default='', server_default=''),
               )

# seed ids for user crawling
seed_ids = Table('seed_ids', metadata,
                 Column("id", INTEGER, primary_key=True, autoincrement=True),
                 Column("uid", String(20), unique=True),
                 Column("is_crawled", INTEGER, default=0, server_default='0'),
                 Column("other_crawled", INTEGER, default=0, server_default='0'),
                 Column("home_crawled", INTEGER, default=0, server_default='0'),
                 Column("update_time", INTEGER, default=0, server_default='0'),
                 )

# search keywords table
keywords = Table('keywords', metadata,
                 Column("id", INTEGER, primary_key=True, autoincrement=True),
                 Column("keyword", String(200), unique=True),
                 Column("enable", INTEGER, default=1, server_default='1'),
                 )

# 微博信息表 weibo_data
weibo_data = Table('weibo_data', metadata,
                   Column("id", INTEGER, primary_key=True, autoincrement=True),
                   Column("weibo_id", String(200), unique=True),
                   Column("weibo_cont", String(6000), default='', server_default=''),
                   Column("repost_num", INTEGER, default=0, server_default='0'),
                   Column("comment_num", INTEGER, default=0, server_default='0'),
                   Column("praise_num", INTEGER, default=0, server_default='0'),
                   Column("uid", String(20)),
                   Column("is_origin", INTEGER, default=1, server_default='1'),
                   Column("device", String(200), default='', server_default=''),
                   Column("weibo_url", String(300)),
                   Column("create_time", String(200)),
                   Column("comment_crawled", INTEGER, default=0, server_default='0'),
                   Column("repost_crawled", INTEGER, default=0, server_default='0'),
                   )

# keywords and weibodata relationship
keywords_wbdata = Table('keywords_wbdata', metadata,
                        Column("id", INTEGER, primary_key=True, autoincrement=True),
                        Column("keyword_id", INTEGER),
                        Column("wb_id", String(200)),
                        )

# comment table
weibo_comment = Table('weibo_comment', metadata,
                      Column("id", INTEGER, primary_key=True, autoincrement=True),
                      Column("comment_id", String(50)),
                      Column("comment_cont", String(5000)),
                      Column("weibo_id", String(200)),
                      Column("user_id", String(20)),
                      Column("create_time", String(200)),
                      )

# repost table
weibo_repost = Table("weibo_repost", metadata,
                     Column("id", INTEGER, primary_key=True, autoincrement=True),
                     Column("user_id", String(20)),
                     Column("user_name", String(200)),
                     Column("weibo_id", String(200), unique=True),
                     Column("parent_user_id", String(20)),
                     Column("repost_time", String(200)),
                     Column("repost_cont", String(5600), default='', server_default=''),
                     Column("weibo_url", String(200)),
                     Column("parent_user_name", String(200)),
                     Column("root_weibo_id", String(200)),
                     )

# relations about user and there fans and follows
user_relation = Table("user_relation", metadata,
                      Column('id', INTEGER, primary_key=True, autoincrement=True),
                      Column('user_id', String(20)),
                      Column('follow_or_fans_id', String(20)),
                      Column('type', INTEGER)  # 1 stands for fans, 2 stands for follows
                      )

# pics in each weibo, one pic one record
weibo_pic = Table("weibo_pic", metadata,
                  Column('id', INTEGER, primary_key=True, autoincrement=True),
                  Column("weibo_id", String(20)),
                  Column("uid", String(12)),
                  Column("pic_url", String(80)),
                  Column("url_hash", String(64)),
                  Column('dl_flag', INTEGER, default=0, server_default='0'),
                  Column('judge_flag', INTEGER, default=0, server_default='0')
                  )


# proxy table
proxys = Table("proxys", proxy_db_metadata,
                  Column('id', INTEGER, primary_key=True, autoincrement=True),
                  Column('ip', VARCHAR(16), nullable=False),
                  Column('port', INTEGER, nullable=False),
                  Column('types', INTEGER, nullable=False),
                  Column('protocol', INTEGER, nullable=False, default=0),
                  Column('country', VARCHAR(100), nullable=False),
                  Column('area', VARCHAR(100), nullable=False),
                  Column('updatetime', DateTime()),
                  Column('speed', Numeric(5, 2), nullable=False),
                  Column('score', INTEGER, nullable=False),
                  Column('last_delta', INTEGER, nullable=False, default=0, server_default='0'),
                  )


__all__ = ['login_info', 'wbuser', 'seed_ids', 'keywords', 'weibo_data', 'keywords_wbdata', 'weibo_comment',
           'weibo_repost', 'user_relation', 'weibo_pic', 'proxys']