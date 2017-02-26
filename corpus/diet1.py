#!/usr/bin/python3
# coding: utf8
from bs4 import BeautifulSoup as bs
import requests
import pymysql
import pickle
import os

"""
大分类中有小分类，小分类中有具体的食物分类
"""
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='shortdata2.1', charset='utf8')
cursor = conn.cursor()
cate1 = ["bjbk/","jjys/","rqss/","ysys/","zyys/","jbtl/"]
main_url= "http://jk.zuofan.cn/"
headers = {
	"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
	"Connection":"keep-alive"
}


def get_catelinks_in_per_big_cate(main_url,cate1):
		littlecate_links = []
		for x in cate1:
			per_bigcate_url = main_url + x
			response = requests.get(per_bigcate_url,headers = headers)
			response.encoding = 'utf8' #根据网页编码来写
			soup= bs(response.text,'lxml')#body > div.wrap > div.con_middle > div.newslist > ul > li > a
			littlecate_links_labels = soup.select('div.c-healthDiv1 > div > h2 > a') 
			for item in littlecate_links_labels:
					littlecate_links.append(item.get("href"))
		return littlecate_links
		
def get_links_in_per_page(littlecate_links):
	hrefs = []
	for url in littlecate_links:	 	
		response1 = requests.get(url,headers = headers)
		response1.encoding = 'utf8' #根据网页编码来写
		soup1= bs(response1.text,'lxml')
		body_con = soup1.select("body")[0].stripped_strings
	
		if "末页" in body_con:
			last_page_href = soup1.select("li.page-item > a")[-1].get("href") #取末页时，根据链接取到最后一个
			print(last_page_href)
			page_digit = filter(str.isdigit, last_page_href) #href=/bjbk/yyqs/list_268_28.html
			digit_in_href = ''
			for i in page_digit:
    				digit_in_href = digit_in_href + i
			print(digit_in_href)
			if len(digit_in_href) >= 6:
				continue
			else:
				mid_code = digit_in_href[:3]
				last_page_digit = digit_in_href[3:]
				print("***mid_code***"+mid_code)
				print("***last_page_digit{}***".format(last_page_digit))
				urls = [url + "list_{}_{}".format(mid_code,str(i))+".html" for i in range(1,int(last_page_digit)+1)]
				for href in urls:
						per_response = requests.get(href,headers = headers)
						per_response.encoding = 'utf8' #根据网页编码来写
						per_soup= bs(per_response.text,'lxml')
						links = per_soup.select('div.b_healthA1 > dl > dt > a')  
						for link in links:
							href = link.get("href")  #/guopin/shuiguo/yaguangli/
							hrefs.append(href)

		else:
			per_response1 = requests.get(url,headers = headers)
			print("else:")
			per_response1.encoding = 'utf8' #根据网页编码来写
			per_soup1= bs(per_response1.text,'lxml')
			links1 = per_soup1.select('div.b_healthA1 > dl > dt > a')  #div.cateA3 > dl > a > dt > h3  
			for link1 in links1:
				href1 = link1.get("href") #/guopin/shuiguo/yaguangli/
				#print(type(href))
				hrefs.append(href1)
	with open("diet1_all_hrefs.pkl",'wb') as f:
		 pickle.dump({"hrefs":hrefs}, f, pickle.HIGHEST_PROTOCOL)

#print(get_links_in_per_page(cate1,main_url))

def get_text_in_per_page():
	with open('diet1_all_hrefs.pkl', 'rb') as f:
		hrefs_pairs = pickle.load(f)
		hrefs = hrefs_pairs["hrefs"]
		for href in hrefs:
			response2 = requests.get(href,headers = headers)
			response2.encoding = 'utf8' #根据网页编码来写
			soup2 = bs(response2.text,'lxml')
			print("href:"+href)

			question = soup2.select('.a-a-healthH22')[0].get_text() 
			print(question)
			answers_list =[i.get_text() for i in soup2.select("#articleadbox > div")]
			#answers= answers.encode("utf8")

			if answers_list==[]: 
				answers_list = [i for i in soup2.select("#articleadbox")[0].strings]
			answers = ""     #末页li.page-item > a

			for x in answers_list:
				answers = answers + x +"\n"	
			print(answers)	
			sql = "INSERT ignore INTO `shortdata2.1`.short_corpus(question,answer) VALUES(%s,%s)"
			cursor.execute(sql,(question, answers))
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
	