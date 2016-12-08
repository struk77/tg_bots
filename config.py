#!/usr/bin/python3
import datetime

token = 'YOUR_BOT_TOKEN'
weather_api = 'YOUR_OWM_TOKEN'

ECHO = 0
USER = ''
CHAT_USER = {'':''}
USER_ECHO = {'':''}

LAST_PHRASE = ''

STOPPED = {0:False}

CHAT_TIME = {0:datetime.date.today()}

isGo = {}

thread = 0

cities = {'1':'Kyiv,ua', '2':'Riga,lv', '3':'Sankt-Peterburg,ru'}

advice = {}

news = ''
