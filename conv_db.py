#!/usr/bin/python3

import pymysql
import re
import feedparser

def write_conv(chat_id, user_id, message):
	db = pymysql.connect(host="localhost", user="spisok", passwd="spisok", db="spisok", charset='utf8')
	cursor = db.cursor()
	sql = """INSERT INTO conversation(chat_id, user_id, message)
        VALUES ('%(chat_id)s', '%(user_id)s', '%(message)s')
        """%{"chat_id":chat_id, "user_id":user_id, "message":message}
	cursor.execute(sql)
	db.commit()
	db.close()

def get_sentence():
	f = open('spisok_bot.log','r')
	data_list = list(f)
	f.close()
	bd_list = []
	db = pymysql.connect(host="localhost", user="spisok", passwd="spisok", db="spisok", charset='utf8')
	cursor = db.cursor()
	result = cursor.fetchall()
	db.close()

def get_news(n=0):
	import feedparser
	d = feedparser.parse('https://www.reddit.com/r/ukraina/.rss')
	title = d.entries[n].title
	summary = d.entries[n].summary
	summary = summary.split('a href="')[3]
	summary = summary.split('"')[0]
	return title, summary
	
#print(parse_news(2))



	
