#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import numpy as np
from scipy import spatial 
import copy
import logging
import pymysql

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

def get_matrix_full(bd_list):
	word_dict = {}
	index = 0 # Создаём словарь всех уникальных слов в нижнем регистре
	for row in bd_list:
		words = re.split('\W+',row, flags=re.U)
		# Берём только слова длиннее 2 букв
		words = [x for x in words if len(x) > 2]
		for word in words:
			lower_word = word.lower()
			if not lower_word in word_dict:
				word_dict[lower_word] = index
				index += 1

	rows = len(bd_list)
	cols = len(word_dict.values())

	my_matrix = np.zeros((rows,cols))
	line = 0
	for row in bd_list:
		sentence = row.lower()
		words = re.split('\W+',sentence, flags=re.U)
		words = [x for x in words if len(x) > 2]
		for word in words:
			idx = word_dict[word]
			my_matrix[(line,idx)] += 1
		line += 1
	return my_matrix
	
def get_matrix_3(bd_list):
	word_dict = {}
	index = 0
	for row in bd_list:
		words = re.split('\W+',row, flags=re.U)
		words = [x for x in words if len(x) > 2]
		for word in words:
			lower_word = word.lower()
			epoch = len(lower_word) - 2
			list_3 = []
			for i in range(epoch):
				start_pos = i
				end_pos = i + 3
				list_3.append(lower_word[start_pos:end_pos])
			for tr in list_3:
				if not tr in word_dict:
					word_dict[tr] = index
					index += 1
	rows = len(bd_list)
	cols = len(word_dict.values())
	my_matrix = np.zeros((rows,cols))
	line = 0
	for row in bd_list:
		sentence = row.lower()
		words = re.split('\W+',sentence, flags=re.U)
		words = [x for x in words if len(x) > 2]
		for word in words:
			epoch = len(word) - 2
			list_3 = []
			for i in range(epoch):
				start_pos = i
				end_pos = i + 3
				list_3.append(word[start_pos:end_pos])
			for tr in list_3:
				idx = word_dict.get(tr)
				my_matrix[(line,idx)] += 1
		line += 1
	return my_matrix
	
def write_log(text1,text2="",text3=""):
	with open("/home/pobeda/projects/tg_bots/spisok/conv_log.txt", "a") as fout:
		text = text1 + "\n" + text2 + "\n" + text3 + "\n" + "******" + "\n"
		fout.write(text)

def get_sentence(last):

	db = pymysql.connect(host="localhost", user=USERNAME, passwd=PASSWORD, db=DATABASE, charset='utf8')
	cursor = db.cursor()
	
	# Выбираем уникальные фразы из лога
	cursor.execute("SELECT message FROM conversation")
	
	# Загоняем их в массив
	bd_list = []
	for row in cursor:
		result = cursor.fetchone()
		#print(result[0])
		if result != None:
			bd_list.append(result[0])
	db.close()
	
	my_matrix = get_matrix_3(bd_list)
		
	cos_list = []
	for row in my_matrix:
		cos_dist = spatial.distance.cosine(my_matrix[last],row)
		cos_list.append(cos_dist)
	cos_list_2 = copy.copy(cos_list)
	cos_list_2.sort()
	min1 = cos_list_2[1]
	min2 = cos_list_2[2]
	index1 = cos_list.index(min1)
	index2 = cos_list.index(min2)
	write_log(bd_list[-1],bd_list[index1],bd_list[index1+1])
	return (bd_list[index1])
	
