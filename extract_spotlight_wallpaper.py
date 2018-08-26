#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: extract_spotlight_wallpaper.py
# Created Date: 2018-08-25 16:20:42
# Author: canalStar
# -----
# Last Modified: 2018-08-26 13:28:25
# Last Modified By: canalStar
###

""" 将windows10 锁屏spotlight壁纸提取出来，并将竖屏与横屏文件夹，分开存放
    1.读取当前目录中的记录文件，如果没有则新建一个
    2.将spotlight文件夹中记录文件夹中不存在的且大于300k的文件提取到临时文件夹中，并重命名为.jpg格式
    3.读取文件分辨率，将分辨率为1920*1080与1080*1920的图片分别移动到不同的文件夹中，并将所移动的文件名
      记录在log文件中，下次提取时就可略过这些文件
    4.删除临时文件夹
"""
import os
import csv
import shutil
from PIL import Image


def select_move(source_dir, temp_dir, log_set, hori_dir, vert_dir):
    """
        筛选源文件夹中所有大于300k且不在log_set中的文件移入temp_dir文件夹,并添加后缀名.jpg
        输入参数：源文件夹名称，目标文件夹名称，已完成文件记录的集合
        输出参数：新添加的文件记录构成的集合
    """
    new_set = set()
    files = os.listdir(source_dir)
    for file in files:
        source_file = os.path.join(source_dir, file)
        if not os.path.isdir(source_file):
            fsize = os.path.getsize(source_file)/1024
            if (fsize>300) and not(file in log_set):
                new_set.add(file)
                temp_file = os.path.join(temp_dir, file+".jpg")
                shutil.copyfile(source_file, temp_file)
                classify(file,temp_file, hori_dir, vert_dir)
    print(len(new_set))
    return new_set


def classify(filename, temp_file, hori_dir, vert_dir):
    """根据图片的分辨率将壁纸分配到水平壁纸或者竖直壁纸两个文件夹"""
    img = Image.open(temp_file)
    imsize = img.size
    img.close()
    hori = (1080, 1920)
    vert = (1920, 1080)
    if imsize == hori:
        shutil.move(temp_file, os.path.join(hori_dir, filename+".jpg"))
    elif imsize == vert:
        shutil.move(temp_file, os.path.join(vert_dir, filename+".jpg"))
    return


def append_newlog(log_file, new_set):
    """
        将集合中的数据附加到log.csv文件的末尾进行记录
        输入：log_file的绝对路径，需要添加的新的记录构成的集合
    """
    #print(list(new_set))
    with open(log_file, 'a+') as csvfile:
        for item in new_set:
            csvfile.write(item)
            csvfile.write(",")
        #writer.writerow(new_set)
            

if __name__ == "__main__":

    # 获取当前的用户主目录
    home = os.path.expanduser('~')
    # 主目录添加上spotlight壁纸的相对路径，构成壁纸源路径
    source_dir = os.path.join(
        home, r"AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets")
    # 目标目录
    dest_dir = os.path.join(home, r"Pictures\WallPapers")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 临时目录
    temp_dir = os.path.join(dest_dir, r"temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # 根据分辨率设置不同的子目录
    hori_dir = os.path.join(dest_dir, r"horizontal")  # 竖屏1080*1920
    vert_dir = os.path.join(dest_dir, r"vertical")  # 横屏1920*1080
    if not os.path.exists(hori_dir):
        os.makedirs(hori_dir)
    if not os.path.exists(vert_dir):
        os.makedirs(vert_dir)

    # 设置log文件的位置
    log_file = os.path.join(dest_dir, r"log.csv")
    # 创建空集合，用于存储文件中的记录
    log_set = set()
    # 判断目标目录下有无历史记录文件，如果存在则读取其内容至set
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_reader = f.read()
            list_result = log_reader.split(",")
            for item in list_result:
                if item !="":
                    log_set.add(item)
  

    # 遍历源文件夹并将其中符合要求的文件移入临时文件夹
    new_set = select_move(source_dir, temp_dir, log_set,hori_dir, vert_dir)

    #将new_set添加到log.csv文件末尾
    append_newlog(log_file, new_set)

    #删除临时文件夹
    shutil.rmtree(temp_dir)
