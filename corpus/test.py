#!/usr/bin/python3
# coding: utf8
from bs4 import BeautifulSoup as bs
import requests

main_url= "http://www.zuofan.cn/?404&/caipu/xiaochi/118000.html"
response2 = requests.get(main_url)
at = response2.status_code
print(at)
response2.encoding = 'utf8' #根据网页编码来写
soup2 = bs(response2.text,'lxml')
#print(soup2,file = open('xiaozhu.txt','w',encoding = 'utf8'))  .healthH22
content_in_all_page = soup2.select("body")[0].stripped_strings
if "菜系" and "小吃" in content_in_all_page:
    print("过滤")
else:
    print(content_in_all_page)


  "mian/chaofan/", "rou/niurou/","rou/yangrou/",\
"rou/jirou/","rou/yarou/","rou/yurou/","rou/hongshaorou/","rou/paigu/","rou/jidan/","rou/yadan/","mian/miantiao/","mian/mantou/","mian/baozi/", "mian/mianshi/","mian/fen/",\
"mian/mixian/","mian/jiaozizuofa/","mian/gjf/","mian/zhou/","caipu/zaocan/","caipu/wucan/","caipu/wancan/","caipu/xiafan/","caipu/kuaishou/","caipu/jiachangcai/","caipu/recai/","caipu/huncai/","caipu/liangcai/","caipu/xiaochi/",\
"caixi/lucai/","caixi/chuancai/","caixi/yuecai/","caixi/mincai/","caixi/sucai/","caixi/zhecai/","caixi/xiangcai/","caixi/huicai/","caixi/jingcai/shc/","rou/zhurou/",