#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import numpy as np
from scipy import spatial 
import copy
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

def get_sentence(last):
	f = open('/var/log/spisok_bot.log','r')
	data_list = list(f)
	f.close()
	
	# Создаём список всех сообщений. Объединяем многострочные сообщения в одно.
	bd_list = []
	for s in data_list:
		s = re.split('::', s)
		if len(s) < 3:
			str = bd_list[-1]
			bd_list[-1] = str + s[0]
		else:
			if s[0][0] == "-" and s[0][1][0] != 'U':
				bd_list.append(s[2])
	
	# Создаём словарь всех уникальных слов в нижнем регистре
	word_dict = {}
	index = 0
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
	#logger.info(bd_list[-1])
	#logger.info(bd_list[index1+1])
	return (bd_list[index1])
