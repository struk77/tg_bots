#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import telegram
import config, solar, conversation, weather
import pyowm
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

LOCATION = 0
ECHO = 0
USER = ''

magic_name_dict = config.magic_name_dict

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def getWeather(lat, lon):
	weather_api = weather.weather_api
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
	f = open('test.log','a')
	f.write(line)
	f.close()

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
	#logger.info(chat)
	user = str(update.message.from_user.id)
	message = update.message.text
	log_conversation(chat,user,message)
	if USER == user:
		ECHO+=1
		if ECHO > random.choice([2,3]):
			text = conversation.get_sentence(-1)
			update.message.reply_text(text)
	else:
		ECHO = 0
	
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

	# Start the Bot
	#updater.start_polling()

	# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	#updater.idle()
	
	updater.start_webhook(listen='127.0.0.1', port=5001, url_path=config.token)
	#updater.bot.setWebhook(url='https://strukkk.tk/'+config.token, certificate=open('/etc/letsencrypt/live/www.strukkk.tk/cert.pem', 'rb'))


if __name__ == '__main__':
	main()