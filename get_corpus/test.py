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




 ["xiaochi/bfxc/","xiaochi/nfxc/",\
"xiaochi/scxc/","xiaochi/chongq/","xiaochi/bjxc/","xiaochi/tjxc/","xiaochi/twxc/","xiaochi/hk/",\
"xiaochi/shanx/","xiaochi/hanxi/","xican/yidali/","xican/faguocai/","xican/taiguocai/","xican/yindu/","xican/hanguocai/","xican/haixian/","xican/xibanya/","xican/dny/","xican/riben/",\
"xican/shousi/","tang/jidantang/","tang/gedatang/","tang/jiyutang/","tang/haixiantang/","tang/paigutang/","tang/shoushentang/","tang/meirong/","tang/yangsheng/","tang/tianpin/","tang/dunpin/",\
"hongbei/mianbao/","hongbei/binggan/","hongbei/quqi/","hongbei/dangao/","hongbei/tusi/","hongbei/pizza/","hongbei/yuebing/","jiankang/youer/","jiankang/yinger/","jiankang/er/","jiankang/baoshipu/",\
"jiankang/beiyun/","jiankang/chan/","jiankang/muying/","jiankang/laoren/","pengren/shaokao/","pengren/huoguo/","pengren/zhengzhi/","pengren/dunzhi/","pengren/yanzhi/","pengren/zhazhi/","pengren/luzhi/",\
"pengren/xunzhi/","pengren/jian/","pengren/hongshao/","kouwei/mala/","kouwei/suanla/","kouwei/wuxiang/","kouwei/qingdan/","kouwei/tiangcu/","kouwei/jiangx/","kouwei/suanxiang/","kouwei/kali/",\
"kouwei/ziran/","kouwei/jiaoyan/","jieri/nianye/","jieri/zhongqiu/","jieri/tangyuanzuofa/","jieri/laba/","jieri/duanwujie/","jieri/chongy/","jieri/chun/","jieri/xia/","jieri/qiu/","jieri/dong/"]