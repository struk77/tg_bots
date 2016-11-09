#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import telegram
import config, solar, conversation, uksus
import pyowm
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import random


from PIL import Image
import numpy as np
import urllib


LOCATION = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def getWeather(lat, lon):
	weather_api = config.weather_api
	owm = pyowm.OWM(weather_api)
	observation_list = owm.weather_around_coords(lat, lon)
	observation = observation_list[0]
	l = observation.get_location().get_name()
	w = observation.get_weather()
	s = w.get_status()
	t = w.get_temperature('celsius').get('temp')
	result = {'city':l,'status':s,'temp':str(t)}
	return result
	
def log_conversation(chat,user,message):
	line = chat + '::' + user + '::' + message + "\n"
	f = open('/var/log/spisok_bot.log','a')
	f.write(line)
	f.close()
	
def global_echo(echo, user):
	return echo

def start(bot, update):
	update.message.reply_text('Hi!')

def help(bot, update):
	update.message.reply_text('Help!')

def dt(bot, update):
	user = update.message.from_user
	logger.info("User %s wants to know the price of solar." % user.first_name)
	text = 'On KLO solar costs '
	text = text + str(solar.parse_klo())
	text = text + " UAH"
	update.message.reply_text(text)
	
def weather(bot, update):
	user = update.message.from_user
	logger.info("User %s wants to know the weather." % user.first_name)
	update.message.reply_text('Send me your location please, '
							  'or send /skip if you don\'t want to.')
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

def echo(bot, update):

	chat = str(update.message.chat.id)
	user = str(update.message.from_user.id)
	message = update.message.text

	log_conversation(chat,user,message)
	
	if chat not in config.CHAT_USER:
		config.CHAT_USER[chat] = user
		config.USER_ECHO[user] = 0
	else:
		if config.CHAT_USER[chat] == user:
			config.USER_ECHO[user] += 1
			if config.USER_ECHO[user] > random.choice([1,2]):
				if random.choice([True,False]):
					text = conversation.get_sentence(-1)
				else:
					username = uksus.get_name(user)
					text = uksus.get_phrase(username)
				update.message.reply_text(text)
		else:
			config.USER_ECHO[user] = 0
			config.CHAT_USER[chat] = user
	#logger.info(chat + " " + user + " " + config.CHAT_USER[chat])
	
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
	pid = os.getpid()
	#os.kill(pid,1)

def radar_kiev(bot, update):

    # send typing...
    bot.sendChatAction(action=telegram.ChatAction.TYPING,chat_id=update.message.chat_id)

    pngfile="/tmp/UKBB_latest.png"
    pngtransfile="/tmp/UKBB_transparent.png"
    output="/tmp/output.png"
    mapfile="map.png"

    # get radar black-white png
    urllib.urlretrieve("http://meteoinfo.by/radar/UKBB/UKBB_latest.png", pngfile)

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
    with open(output,'r') as photo_file:
          update.message.reply_photo(photo_file)


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
						CommandHandler('skip', skip_location)]
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("dt", dt))
	dp.add_handler(CommandHandler("stop", stop))
	dp.add_handler(conv_handler)

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler(Filters.text, echo))

	# log all errors
	dp.add_error_handler(error)

	updater.start_webhook(listen='127.0.0.1', port=5001, url_path=config.token)

if __name__ == '__main__':
	main()