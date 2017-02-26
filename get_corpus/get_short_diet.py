#!/usr/bin/python3
# coding: utf8
from bs4 import BeautifulSoup as bs
import requests
import pymysql
import time

"""
大分类中有小分类，小分类中有具体的食物分类
"""
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='shortdata2', charset='utf8')
cursor = conn.cursor()

main_url= "http://sc.zuofan.cn/"
headers = {
	"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
	"Connection":"keep-alive"
}


def get_big_cate_page(main_url):
	cate_links = []
	response = requests.get(main_url,headers = headers)
	response.encoding = 'utf8' # 根据网页编码来写
	soup= bs(response.text,'lxml') # body > div.wrap > div.con_middle > div.newslist > ul > li > a
	cate_links_labels = soup.select('div.listDiv1 > dl > dt > h3 > a')
	for item in cate_links_labels:
			cate_links.append(item.get("href"))
	return cate_links

def get_links_in_per_page(cate_links):
	hrefs = []
	for url in cate_links:	 	
		response1 = requests.get(url,headers = headers)
		response1.encoding = 'utf8' #根据网页编码来写
		soup1= bs(response1.text,'lxml')
		body_con = soup1.select("body")[0].stripped_strings
	
		if "末页" in body_con:
			last_page_href = soup1.select("li.page-item > a")[-1].get("href") #取末页时，根据链接取到最后一个
			print(last_page_href)
			page_digit = filter(str.isdigit, last_page_href) #href="http://sc.zuofan.cn/wugu/mmzp/list_604_6.html"
			digit_in_href = ''
			for i in page_digit:
    				digit_in_href = digit_in_href + i
			print(digit_in_href)
			mid_code = digit_in_href[:3]
			last_page_digit = digit_in_href[3:]
			print("***mid_code***"+mid_code)
			print("***last_page_digit{}***".format(last_page_digit))
			urls = [url + "list_{}_{}".format(mid_code,str(i))+".html" for i in range(1,int(last_page_digit)+1)]
			for href in urls:
					per_response = requests.get(href,headers = headers)
					per_response.encoding = 'utf8' #根据网页编码来写
					per_soup= bs(per_response.text,'lxml')
					links = per_soup.select('div.cateA3 > dl > a')  
					for link in links:
						href = link.get("href")  #/guopin/shuiguo/yaguangli/
						hrefs.append(main_url[:-1]+href)

		else:
			per_response1 = requests.get(url,headers = headers)
			print("else:")
			per_response1.encoding = 'utf8' #根据网页编码来写
			per_soup1= bs(per_response1.text,'lxml')
			links1 = per_soup1.select('div.cateA3 > dl > a')  #div.cateA3 > dl > a > dt > h3  
			for link1 in links1:
				href1 = link1.get("href") #/guopin/shuiguo/yaguangli/
				#print(type(href))
				hrefs.append(main_url[:-1]+href1)
	print(hrefs)
	return hrefs

#print(get_links_in_per_page(cate1,main_url))

def get_text_in_per_page(hrefs):
	for href in hrefs:
		response2 = requests.get(href,headers = headers)
		response2.encoding = 'utf8' #根据网页编码来写
		soup2 = bs(response2.text,'lxml')
		#print(soup2,file = open('xiaozhu.txt','w',encoding = 'utf8'))  .healthH22
		print("begin!!")
		question_labels = soup2.select('div.detailsDiv3 > h3')[:-1]
		answers = soup2.select("div.detailsDiv3")[1:9] 
		print(answers)
		
		for question_label, answer in zip(question_labels,answers):
				question = question_label.get_text()
				print("question {}".format(question))
				answer_zong = ""
				for x in answer.strings:
					answer_zong = answer_zong + x
				#answers= answers.encode("utf8")
				print("answer {}".format(answer_zong))
				sql = "INSERT ignore INTO shortdata2.short_corpus(question,answer) VALUES(%s,%s)"
				cursor.execute(sql,(question, answer_zong))
				conn.commit()
				
if __name__ == '__main__':
	littlecate_links = get_big_cate_page(main_url)
	urls = get_links_in_per_page(littlecate_links)
	get_text_in_per_page(urls)
	
	cursor.close()
	
	conn.close()
	