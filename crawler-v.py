# -*- coding: utf-8 -*-  

import logging
from logging.handlers import RotatingFileHandler
import sqlite3
from datetime import date
import time
import requests
from lxml import html
#import cookielib
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('logs/weibo.log', 'a', 1000000, 1)
file_handler.setLevel( logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

username = "virginie.julliard@gmail.com"
password = "digitaleternity"
#header = {'User-Agent':"Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"}
header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.103 Safari/537.36'}

def main():
	return_value = 0
	db_conn = None
	
	try:
		db_conn = sqlite3.connect("weibo.db")
		db_cursor = db_conn.cursor()
		deadusers = []
		for row in db_cursor.execute('select name, id, year, month, day from deaduser where done=0'):
			year = row[2]
			month = row[3]
			day = row[4]
			if day == 0:
				deadusers.append({'name': row[0], 'id': row[1], 'died': date(year, month, 1)})
			else:
				deadusers.append({'name': row[0], 'id': row[1], 'died': date(year, month, day)})
		
		#login
		s = requests.session()
		url = "http://login.weibo.cn/login/"
		r = s.get(url, headers=header)
		r.raise_for_status()
		result = html.fromstring(r.text.split('<?xml version="1.0" encoding="UTF-8"?>')[1])
		pswd_field = result.xpath(".//input[@type='password']/@name")[0]
		vk = result.xpath(".//input[@name='vk']/@value")[0]
		payload = {
			'mobile': username,
			pswd_field: password,
			'remember':'checked',
			'backURL': 'http%3A%2F%2Fweibo.cn',
			'backTitle': '手机新浪网',
			'vk': vk,
			'submit': '登录'
		}
		action = result.xpath(".//form/@action")[0]
		url = "%s%s"% (url, action)
		s.post(url, headers=header, data=payload)
	
		        
		for deaduser in deadusers: 
			page = 0
			totalmsg = 0
			needmore = True
			logger.info("STARTING user %s (%d)"% (deaduser['name'], deaduser['id']))
			while needmore:
				page += 1
				url = "http://weibo.cn/n/%s?page=%d"% (deaduser['name'], page)
				try:
					r = s.get(url, headers=header)
					r.raise_for_status()
				except Exception as e:
					logger.error("Could not get page %d for dead user %s"% (page, deaduser))
					logger.error(e, exc_info=True)
					needmore = False
				else:
					text = r.text.split('<?xml version="1.0" encoding="UTF-8"?>')[1]
					result = html.fromstring(text)
					f = open("pages/%s-page%d.html"% (deaduser['id'], page), 'w+')
					f.write(html.tostring(result))
					f.close()
					
					messages = []
					onebeforedeath = False
					if len(result.xpath('//*[@class="c"]/@id')) == 0:
						needmore = False
						db_cursor.execute('update deaduser set done=1 where name=?', [deaduser['name']])
						db_conn.commit()
						logger.info("====== user %s (%s) - %d messages ====="% (deaduser['name'], deaduser['died'].strftime("%Y-%m-%d"), totalmsg))
							
					else:
						for i in range(0, len(result.xpath('//*[@class="c"]'))):
							if needmore:
								if len(result.xpath('//*[@class="c"][%d]/@id'% (i+1))) > 0:
									d = result.xpath('//*[@class="c"][%d]//*[@class="ct"]'% (i+1))[0].text.split(" ")[0]
									ymd = d.split("-")
									if len(ymd) < 3:
										if len(d) == 6:
											d = "2014-%s-%s"% (d[:2], d[3:-1])
											ymd = d.split("-")
									if len(ymd) == 3:
										year = ymd[0]
										month = ymd[1]
										day = ymd[2]
										created_at = date(int(year), int(month), int(day))
										hour = result.xpath('//*[@class="c"][%d]//*[@class="ct"]'% (i+1))[0].text.split(" ")[1].split(u'\xa0')[0]
										mid = result.xpath('//*[@class="c"][%d]/@id'% (i+1))[0]
										logger.debug("%s :: %s-%s-%s %s"% (mid, year, month, day, hour))
										if (created_at - deaduser['died']).days >= 0:
											params = [mid, year, month, day, hour, deaduser['name']]
											db_cursor.execute('replace into msg2 (mid, year, month, day, hour, name) values (?, ?, ?, ?, ?, ?)', params)
											db_conn.commit()
											totalmsg += 1
										else:
											if onebeforedeath:
												if totalmsg < 3:
													params = [mid, year, month, day, hour, deaduser['name']]
													db_cursor.execute('replace into msg2 (mid, year, month, day, hour, name) values (?, ?, ?, ?, ?, ?)', params)
													db_conn.commit()
													totalmsg += 1
												else:
													needmore = False
													db_cursor.execute('update deaduser set done=1 where name=?', [deaduser['name']])
													db_conn.commit()
													logger.info("====== user %s (%s) - %d messages ====="% (deaduser['name'], deaduser['died'].strftime("%Y-%m-%d"), totalmsg))
											else:
												params = [mid, year, month, day, hour, deaduser['name']]
												db_cursor.execute('replace into msg2 (mid, year, month, day, hour, name) values (?, ?, ?, ?, ?, ?)', params)
												db_conn.commit()
												totalmsg += 1
												onebeforedeath = True
									
			time.sleep(30)
									
	except Exception as e:
		logger.critical(e, exc_info=True)
		return_value = 1
	finally:
		if db_conn<> None:
			db_conn.close()
		return return_value


if __name__ == "__main__":
	logger.critical("START")
	res = main()
	logger.critical("STOP (%d)"% res)
	sys.exit(res)
