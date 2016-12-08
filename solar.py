#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import lxml.html

def parse_klo(data):
	url = 'http://klo.ua/'
	page = requests.get(url).text   
	parser = lxml.html.fromstring(page)     
	divs = parser.find_class('oil-table__price')
	if data=='diesel':
		result = divs[6].text
	else:
		result = divs[0].text
	return result

def parse_lv():
	url = 'https://www.statoil.lv/lv_LV/pg1334072745785/private/Degviela/degvielas-cenas.html'
	page = requests.get(url).text
	parser = lxml.html.fromstring(page)
	table_price = parser.find_class('fuelprices')
	return table_price[0][1][3][1].text

