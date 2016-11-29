#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import config, conversation, uksus, maidan, conv_db
from solar import parse_klo, parse_lv
from hosts import get_status
import pyowm
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
import random
import datetime
import threading,time


from PIL import Image
import numpy as np
import urllib


LOCATION = 0
NEWS = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def getWeather(lat, lon, city=' '):
	weather_api = config.weather_api
	owm = pyowm.OWM(weather_api)
	if city == ' ':
		observation_list = owm.weather_around_coords(lat, lon)
		observation = observation_list[0]
	else:
		observation = owm.weather_at_place(city)
	l = observation.get_location().get_name()
	w = observation.get_weather()
	s = w.get_status()
	t = w.get_temperature('celsius').get('temp')
	result = {'city':l,'status':s,'temp':str(t)}
	return result
	
def log_conversation(chat,user,message):
	conv_db.write_conv(chat,user,message)
	
def global_echo(echo, user):
	return echo

def go(bot, update, chat_id = 0):
	if chat_id == 0:
		chat_id = update.message.chat.id
	if not config.isGo.get(chat_id):
		config.isGo[chat_id] = True
		config.thread = threading.Thread(target=status_auto, args=(bot,update))
		config.thread.start()
	else:
		logger.warn('Thread already running in chat %s' % chat_id)
	
def start(bot, update):
	update.message.reply_text('Hi!')

def help(bot, update):
	update.message.reply_text('Help!')

def status(bot, update, auto=False, array=[]):
	if not auto:
		chat_ids = []
		chat_ids.append(update.message.chat.id)
		user = update.message.from_user
		logger.info("User %s wants to know the status of hosts." % user.first_name)
		array = get_status()
	else:
		chat_ids = [-22637806,90136176]
		logger.info("Autostatus of hosts " + str(chat_ids))
	text = 'Current status of connections is:' + "\n"
	for host in array:
		text = text + host['description']+' is down' + "\n"
	for chat_id in chat_ids:
		bot.sendMessage(chat_id=chat_id, text=text)

def status_auto(bot, update):
	bool = True
	array_old = []
	while bool:
		current_hour = datetime.datetime.now().timetuple()[3]
		if current_hour > 6 and current_hour < 21:
			array = get_status()
			if array != array_old:
				logger.warn('Some shit happens')
				status(bot, update, auto=True, array=array)
			array_old = array
		time.sleep(600)
		
def dt(bot, update):
	user = update.message.from_user
	logger.info("User %s wants to know the price of solar." % user.first_name)
	text = 'On KLO solar costs '
	text = text + str(parse_klo())
	text = text + " UAH" + "\n"
	text2 = 'On StatOil solar costs '
	text2 = text2 + parse_lv()
	text = text + text2
	update.message.reply_text(text)

def news(bot, update):
	user = update.message.from_user
	chat_id = update.message.chat.id
	logger.info("User %s wants to know news." % user.first_name)
	#text = maidan.get_news()
	n = random.randint(0,15)
	title, summary = conv_db.get_news(n)
	config.news = summary
	bot.sendMessage(chat_id=chat_id, text=title)
	update.message.reply_text('r u w\'nna /continue to read, '
							  'or send /skip if u r\'nt.')
	return NEWS
							  
def cont(bot, update):
	#logger.info("hohoho")
	update.message.reply_text(config.news)
	return ConversationHandler.END

def skip_news(bot, update):	
	#logger.info("hehehe")
	update.message.reply_text('Ну и правильно. Не новость, а дрянь какая-то')
	return ConversationHandler.END

def kiev_radar(bot, update):
	# send typing...
	bot.sendChatAction(action=telegram.ChatAction.TYPING,chat_id=update.message.chat_id)

	pngfile="/tmp/UKBB_latest.png"
	pngtransfile="/tmp/UKBB_transparent.png"
	output="/tmp/output.png"
	mapfile="/tmp/map.png"

	# get radar black-white png
	urllib.request.urlretrieve("http://meteoinfo.by/radar/UKBB/UKBB_latest.png", pngfile)

	orig_color = (204,204,204,255)
	replacement_color = (255,255,255,0)
	img = Image.open(pngfile).convert('RGBA')
	data = np.array(img)

	# replace gray colors with transparent
	colors=[204,192]

	for color in colors:
	  orig_color = (color,color,color,255)
	  data[(data == orig_color).all(axis = -1)] = replacement_color

	img2 = Image.fromarray(data, mode='RGBA')
	img2.save(pngtransfile)

	background = Image.open(mapfile).convert('RGBA')
	foreground = Image.open(pngtransfile)

	# merge map with radar png
	background.paste(foreground,(3,10),foreground)
	background.save(output)

	# send it as answer
	with open(output,'rb') as photo_file:
		  update.message.reply_photo(photo_file)

	
def weather(bot, update):
	user = update.message.from_user
	chat_id = update.message.chat.id
	logger.info("User %s wants to know the weather." % user.first_name)
	keyboard = [[InlineKeyboardButton("Kyiv", callback_data='Kiev,ua'),
			InlineKeyboardButton("Riga", callback_data='Riga,lv')],
			[InlineKeyboardButton("Leningrad", callback_data='Sankt-Peterburg,ru'),
			InlineKeyboardButton("Dnipro", callback_data='Dnipropetrovsk,ua')]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Please choose or send your location or /skip:', reply_markup=reply_markup)
		#update.message.reply_text('Send me your location please, '
		#					  'or send /skip if you don\'t want to.')
	return LOCATION
	
def location(bot, update):
	user = update.message.from_user
	user_location = update.message.location
	logger.info("Location of %s: %f / %f"
				% (user.first_name, user_location.latitude, user_location.longitude))
	w = getWeather(user_location.latitude,user_location.longitude)
	text = 'Now in ' + w.get('city') + ' is ' + w.get('status')
	text = text + '. Temperature: ' + w.get('temp') + u"\u2103"
	update.message.reply_text(text)
	return ConversationHandler.END
	
def skip_location(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a location." % user.first_name)
	update.message.reply_text('You seem a bit paranoid! ')
	return ConversationHandler.END

def button(bot, update):
	query = update.callback_query
	logger.info("User wants to know the weather in %s." % query.data)
	w = getWeather(0,0,query.data)
	text = 'Now in ' + w.get('city') + ' is ' + w.get('status')
	text = text + '. Temperature: ' + w.get('temp') + u"\u2103"
	bot.editMessageText(text=text,
		chat_id=query.message.chat_id,
		message_id=query.message.message_id)
	return ConversationHandler.END

def echo(bot, update):
	chat = str(update.message.chat.id)
	user = str(update.message.from_user.id)
	message = update.message.text
	time = update.message.date
	
	log_conversation(chat,user,message)
	delta = datetime.timedelta(minutes=5)
	oldtime = config.CHAT_TIME.get(update.message.chat.id)
	config.CHAT_TIME[update.message.chat.id] = time

	if chat not in config.CHAT_USER:
		config.CHAT_USER[chat] = user
		config.USER_ECHO[user] = 1
	else:
		if config.CHAT_USER[chat] == user:
			if (time-oldtime) < delta:
				config.USER_ECHO[user] += 1
			else:
				config.USER_ECHO[user] = 1
			if config.USER_ECHO[user] > random.choice([2,3]):
				bot.sendChatAction(action=telegram.ChatAction.TYPING,chat_id=update.message.chat_id)
				if random.choice([False,False]):
					text = conversation.get_sentence(-1)
				else:
					username = uksus.get_name(user)
					text = uksus.get_phrase(username)
				update.message.reply_text(text)
		else:
			config.USER_ECHO[user] = 1
			config.CHAT_USER[chat] = user

	
def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.')
	return ConversationHandler.END

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def stop(bot, update):
	user = update.message.from_user
	logger.warn('User %s stopped the script forever.' % user.first_name)
	update.message.reply_text('Прощайте, друзья...')
	#pid = os.getpid()
	#os.kill(pid,1)


def main():
	# Create the EventHandler and pass it your bot's token.
	updater = Updater(config.token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher
	
	# Add conversation handler for weather
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('weather', weather)],
		states={
			LOCATION: [MessageHandler(Filters.location, location),
						CallbackQueryHandler(button),
						CommandHandler('skip', skip_location)]
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)

	# Add conversation handler for news
	conv_handler_n = ConversationHandler(
		entry_points=[CommandHandler('news', news)],
		states={
			NEWS: [CommandHandler('continue', cont),
						CommandHandler('skip', skip_news)]
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CallbackQueryHandler(button))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("dt", dt))
	dp.add_handler(CommandHandler("go", go))
	dp.add_handler(CommandHandler("status", status))
	dp.add_handler(CommandHandler("stop", stop))
	dp.add_handler(CommandHandler("kiev_radar", kiev_radar))
	dp.add_handler(conv_handler)
	dp.add_handler(conv_handler_n)

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler(Filters.text, echo))

	# log all errors
	dp.add_error_handler(error)

	updater.start_webhook(listen='127.0.0.1', port=5001, url_path=config.token)
	
if __name__ == '__main__':
	main()