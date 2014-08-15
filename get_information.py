# -*- coding: utf-8 -*-
import sqlite3
import time
import random
from bs4 import BeautifulSoup
from mid import url_to_mid
import re
import lxml.html as HTML
import sys

'''connect database'''
db_conn = sqlite3.connect('weibo-msg2.db')
db_cursor = db_conn.cursor()
db_cursor.execute('select mid from msg2')
res_mid=db_cursor.fetchall()
j=0
for i in res_mid:
    j=j+1
    MID=url_to_mid(str(i[0]))
    a= str(MID)
    b= "'"+str(i[0])+"'"
    db_cursor.execute('update msg2 set id=%s where mid=%s'%(a,b))
    db_conn.commit()
print 'OK'
print j

