# -*-coding:utf-8 -*-
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.conf import get_db_args
# for proxy database
from config.conf import get_proxy_db_args
# end


def get_engine():
    args = get_db_args()
    connect_str = "{}+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(args['db_type'], args['user'], args['password'],
                                                             args['host'], args['port'], args['db_name'])
    engine = create_engine(connect_str, encoding='utf-8')
    return engine

# for proxydatabse
def get_proxydb_engine():
    args = get_proxy_db_args()
    connect_str = "{}+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(args['db_type'], args['user'], args['password'],
                                                             args['host'], args['port'], args['db_name'])
    engine = create_engine(connect_str, encoding='utf-8')
    return engine

eng = get_engine()
Base = declarative_base()
Session = sessionmaker(bind=eng)
db_session = Session()
metadata = MetaData(get_engine())


proxy_db_eng = get_proxydb_engine()
proxy_session = sessionmaker(bind=proxy_db_eng)
proxy_db_session = proxy_session()
proxy_db_metadata = MetaData(get_proxydb_engine())

# end

# __all__ = ['eng', 'Base', 'db_session', 'metadata']
__all__ = ['eng', 'Base', 'db_session', 'metadata', 'proxy_db_eng', 'proxy_db_session', 'proxy_db_metadata']