#!/usr/bin/python3
# coding: utf8
from bs4 import BeautifulSoup as bs
import requests
import pymysql


"""
大分类中有小分类，小分类中有具体的食物分类
"""
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='data1', charset='utf8')
cursor = conn.cursor()
cate1 = ["caixi/","caipu/","rou/","mian/","xiaochi/","tang/","xican/","hongbei/","jiankang/","jieri/","kouwei/","pengren/"]
main_url= "http://www.zuofan.cn/"
headers = {
	"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
	"Connection":"keep-alive"
}


def get_little_catelinks_in_per_big_cate(main_url,cate1):
		littlecate_links = []
		for x in cate1:
			per_bigcate_url = main_url + x
			response = requests.get(per_bigcate_url,headers = headers)
			response.encoding = 'utf8' #根据网页编码来写
			soup= bs(response.text,'lxml')#body > div.wrap > div.con_middle > div.newslist > ul > li > a
			littlecate_links_labels = soup.select('#cateContentP > h2 > a')
			for item in littlecate_links_labels:
					littlecate_links.append(item.get("href"))
		return littlecate_links

def get_links_in_per_page(littlecate_links):
	hrefs = []
	for url in littlecate_links:		
		response1 = requests.get(url,headers = headers)
		response1.encoding = 'utf8' #根据网页编码来写
		soup1= bs(response1.text,'lxml')#body > div.wrap > div.con_middle > div.newslist > ul > li > a
		links = soup1.select('#banner > div > ul > li > div > div > a')  
		not_found_urls = ["http://www.zuofan.cn/caipu/xiaochi/118000.html","http://www.zuofan.cn/caipu/xiaochi/117581.html","http://www.zuofan.cn/caipu/xiaochi/117570.html",\
		"http://www.zuofan.cn/caixi/qzc/87372.html","http://www.zuofan.cn/caipu/dan/85954.html","http://www.zuofan.cn/caipu/dan/85952.html","http://www.zuofan.cn/caipu/recai/117262.html",\
		"http://www.zuofan.cn/caipu/recai/117260.html","http://www.zuofan.cn/caipu/recai/117251.html","http://www.zuofan.cn/caipu/recai/117233.html","http://www.zuofan.cn/caipu/recai/117226.html",\
		"http://www.zuofan.cn/caipu/recai/117221.html","http://www.zuofan.cn/rou/yurou/25617.html"]
		for link in links:
			href = link.get("href")
			href = main_url[:-1]+href
			if href in not_found_urls:
					continue
			else:
				hrefs.append(href)
	
	with open("diet_all_hrefs.pkl",'wb') as f:
		pickle.dump({"hrefs":hrefs}, f, pickle.HIGHEST_PROTOCOL)
#print(get_links_in_per_page(cate1,main_url))

def get_text_in_per_page(hrefs):
    with open('diet1_all_hrefs.pkl', 'rb') as f:
		hrefs_pairs = pickle.load(f)
		hrefs = hrefs_pairs["hrefs"]
		for href in hrefs:
			response2 = requests.get(href,headers = headers)
			response2.encoding = 'utf8' #根据网页编码来写
			soup2 = bs(response2.text,'lxml')
			print("href:"+href)

			question = soup2.select('.healthH22')[0].get_text() #运行不出来的时候可以尝试直接复制css路径 .healthH22 
			print(question)
			label_generator = soup2.select(".tagstrong")[0].stripped_strings  #
			label = []
			for j in label_generator:
					label.append(j)
			label = ",".join(label[1:])
		
			answer = soup2.select("#articleadbox")   
			answer = answer[0].stripped_strings  # 取到"#articleadbox"标签下的所有内容之后再用stripped_strings来取其之下的内容
			answers = ""

			for x in answer:
				answers = answers + x
			#answers= answers.encode("utf8")
			print(answers)
			sql = "INSERT ignore INTO data1.corpus(label,question,answer) VALUES(%s,%s,%s)"
			cursor.execute(sql,(label, question, answers))
			conn.commit()

if __name__ == '__main__':
	if not os.path.exists("diet1_all_hrefs.pkl"):
    		littlecate_links = get_catelinks_in_per_big_cate(main_url,cate1)
		urls = get_links_in_per_page(littlecate_links)
		get_text_in_per_page()
	else:
		get_text_in_per_page()
		
		cursor.close()
		
		conn.close()
	
	conn.close()
	