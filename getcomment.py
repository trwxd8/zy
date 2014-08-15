# -*-coding: utf8 -*-
from weibo import APIClient   # 导入weibo的APICient类
import json
import time
import logging
import sqlite3
import sys
import traceback

logger=logging.getLogger('get the comments')
formatter=logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s\
                              %(message)s', '%a, %d %b %Y %H:%M:%S',)
file_handler=logging.FileHandler('report1.log')
file_handler.setFormatter(formatter)
stream_handler=logging.StreamHandler(sys.stderr)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

string='JanFebMarAprMayJunJulAugSepOctNovDec'
db_conn = sqlite3.connect('weibo-msg2.db')
db_cursor = db_conn.cursor()              #connect to the database
db_cursor.execute('select id from msg2')
res=db_cursor.fetchall()
print 'desc',db_cursor.description

mids=[]
for line in res:
    for f in line:
        mids.append(f)      #find mid and write it into a list
for i in range(7,9513):        #consider 150 per account 1000 per ip,we can use 6 scripts and accounts
    mid=mids[i]
    mid_s=str(mid)
    logger.warning(i)
    logger.warning(mid)
    for j in range(1,41):
        try:
            jsonFile = open('./Data/%d-%d.json'%(mid, j))
            json_info=json.load(jsonFile)
        except:
            #comment_info=client.status.show.get(id = m)
            #mun2="'"+comment_info['text']+"'"
            #mun1=0
            #mun3=str(m)
            #db_cursor.execute('update msg2 set text=%s,nbcomments=%s where id=%s'%(mun2,mun1,mun3))
            #db_conn.commit()
            #j=j+1
            continue
        else:
            for k in range(0,51):
                try:
                    t=json_info['comments'][k]['text']#text
                    time=json_info['comments'][k]['created_at']#time
                    cid=json_info['comments'][k]['mid']#cid
                    uid=json_info['comments'][k]['user']['idstr']#uid
                    name="'"+json_info['comments'][k]['user']['name']+"'"#name
                    gender="'"+json_info['comments'][k]['user']['gender']+"'"#gender
                    text="'"+t.replace("'","")+"'"
                    months=time[4:7]
                    month=string.find(months)//3+1
                    month_s=str(month)
                    #db_cursor.execute('update main set cid=%s,mid=%s,year=%s,month=%s,day=%s,hour=%s,text=%s,uid=%s,name=%s,gender=%s '%(cid,mid_s,"'"+time[-4:]+"'",month_s,"'"+time[8:10]+"'","'"+time[11:19]+"'",text,uid,name,gender,cid))
                    db_cursor.execute("insert or replace into main values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(cid,mid_s,"'"+time[-4:]+"'",month_s,"'"+time[8:10]+"'","'"+time[11:19]+"'",text,uid,name,gender))
                    db_conn.commit()
                except:
                    continue
            jsonFile.close()
logger.warning("over 1000")        
