#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random

def get_name(id):
	magic_name_dict = {
		'YOUR_USER_ID' : ['name1','name2','name3']
	}
	name_list = magic_name_dict[id]
	return random.choice(name_list)

def get_phrase(name):
	blue_moody_replies = [
		'Я понял! Ты опять набухался?',
		'На курсере своей сраной курсы прошёл уже?',
		'А что об этом пишут на фейсбуке?',
		'Гуляй рвань, тряси лохмотьями!',
		'Хватит', 
		'Отлично, работаем дальше',
		'Ты не поймешь',
		'Твоего мнения никто не спрашивал',
		'Верить никому нельзя',
		'Математика — это не твое',
		'Диван уже дымится',
		'В своей стране и укрыться негде! Нет у Русских Родины, нет Русского Государства',
		'Да ладно!',
		'Перестань, '+name, 
		name+', прекрати срать в чятик!', 
		name+', ну держите себя в руках', 
		'Достатошно, '+name, 
		'Хочешь об этом поговорить?',
		name+', ну не нужно так напрягаться'
	]
	return random.choice(blue_moody_replies)