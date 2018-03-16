#!/usr/bin/env python
# -*- coding=utf-8 -*-

import os
import shutil
import time
import math
import random
import json
from PIL import Image, ImageDraw
from pylab import *
import wda

client = wda.Client()
session = client.session()

def take_screen_shot():
	client.screenshot('./screenshot/screen.png')

# 获取小人位置
def get_person_postion(gray_img_array, width, height):
	cnt = 0
	line_sum = 0
	col_sum = 0
	# 防止分数的干扰
	for line in range(500, height - 500, 3):
		for col in range(50, width - 50, 3):
			if (gray_img_array[line][col] == 0 and
				gray_img_array[line][col - 40] == 0 and
				gray_img_array[line][col + 40] == 0 and
				gray_img_array[line - 40][col] == 0 and
				gray_img_array[line + 40][col] == 0):
				cnt += 1
				line_sum += line
				col_sum += col

	if (cnt == 0):
		raise Exception("Cant find person!")

	# 返回平均位置
	return line_sum/cnt, col_sum/cnt

# 获取下一个跳的方块位置
def get_dest_postion(gray_img_array, width, height):
	for line in range(500, height - 500, 3):
		for col in range(50, width - 50, 3):
			if (abs(gray_img_array[line][col] - gray_img_array[line-1][col]) > 20 and
				abs(gray_img_array[line][col] - gray_img_array[line-1][col]) < 250):
				return line, col

# 处理截图
def process_screen_shot():
	ts = int(time.time())
	im = Image.open('./screenshot/screen.png')
	im.save('{}_{}.jpg'.format('./screenshot/screen.jpg', ts))
	# 获得图像尺寸:
	width, height = im.size
	gray_img = im.convert('L')
	gray_img.save('./screenshot/screen_grayscale.jpg')

	# line 是从上到下，col 是从左到右
	gray_img_array = array(gray_img)
	gray_img_array_bak = array(gray_img)
	for line in range(500, height - 500):
		for col in range(0, width):
			# 先去除噪声
			if (gray_img_array[line][col] > 80):
				gray_img_array[line][col] = 255
			if (gray_img_array[line][col] < 80):
				gray_img_array[line][col] = 0

	im_white = Image.fromarray(gray_img_array)
	im_white.save('./screenshot/screen_white.jpg')

	line, col = get_person_postion(gray_img_array, width, height)
	dest_line, dest_col = get_dest_postion(gray_img_array_bak, width, height)

	print line, col
	print dest_line, dest_col

	draw = ImageDraw.Draw(im)
	draw.line((col, line) + (dest_col, dest_line), fill=2, width=3)
	im.save('{}_{}.jpg'.format('./screenshot/screen_line.jpg', ts))

	distance = sqrt(abs((col - dest_col)*(line - dest_line)))
	return distance

# 跳吧
def jump_a_step(press_time):
	print('press time: {}'.format(press_time))
	session.tap_hold(100, 100, press_time)

if __name__ == "__main__":
	while (True):
		take_screen_shot()
		distance = process_screen_shot()
		jump_a_step(distance * 0.0017)
		time.sleep(1.5)
