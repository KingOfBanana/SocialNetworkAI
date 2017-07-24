from db.wb_pic import get_pic_url_by_limit
import urllib.request
import os
import re

results = get_pic_url_by_limit(100)
size = '/mw1024/'
pic_path = '/home/pic/'
if results:
	for uid, url in results:
		uid_dir_path = pic_path + uid
		if not os.path.exists(uid_dir_path):
			os.mkdir(uid_dir_path)
		pic_name = re.match('.*/thumb150/(.*)', url).group(1)
		url = url.replace('/thumb150/', size)
		f = open(uid_dir_path + '/' + pic_name,'wb')
		req = urllib.request.urlopen('http:' + url)
		buf = req.read()
		f.write(buf)
	

