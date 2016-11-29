#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import lxml.html

def parse_klo():
	url = 'http://klo.ua/'
	page = requests.get(url).text   
	parser = lxml.html.fromstring(page)     
	divs = parser.find_class('p-dp')
	price_strs = divs[0].text_content().split('\n')

	price_1 = int(price_strs[1])
	price_2 = int(price_strs[2])
	price_3 = int(price_strs[4])
	price_4 = int(price_strs[5])
	return price_1 * 10 + price_2 + price_3 / 10.0 + price_4 / 100.0

def parse_lv():
	url = 'https://www.statoil.lv/lv_LV/pg1334072745785/private/Degviela/degvielas-cenas.html'
	page = requests.get(url).text
	parser = lxml.html.fromstring(page)
	table_price = parser.find_class('fuelprices')
	return table_price[0][1][3][1].text
	
