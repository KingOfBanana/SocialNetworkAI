# coding:utf-8
from random import randint

def random_event_occur():
	true_pool = [1, 20]
	random_num = randint(0, 20)
	if random_num in true_pool:
		return True
	else:
		return False