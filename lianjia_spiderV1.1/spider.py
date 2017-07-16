from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import re
import pymongo
import time
from selenium import webdriver
from config import *
from request import request, get_total_page

# 连接数据库
Client = pymongo.MongoClient(MONGO_URL)
db = Client[MONGO_DB]
table = db[MONGO_TABLE]

# 将信息存入数据库
def save_to_mongo(data):
	table.save(data)
	print('插入一条数据成功')

# 提取页面中的信息
def parse_page(area, url):
		html = request(url)
		if html:
			doc = pq(html)
			items = doc('body > div.content > div.leftContent > ul > li').items()
			for item in items:
				all_conflg = item.find('.houseInfo').text().split(' | ')
				if all_conflg[1].find('别墅') != -1:
					del(all_conflg[1])
				if all_conflg[-1].find('有电梯') != -1:
					all_conflg[-1] = '有'
				else:
					all_conflg[-1] = '无'
				page_url = item.find('a.img').attr('href')
				title = item.find('.title').text()
				total_price = item.find('.totalPrice span').text()
				unit_price = item.find('.unitPrice').text()
				loaction = item.find('.positionInfo a').text()
				data = {
					'标题': title,
					'URL': page_url,
					'所在区': area,
					'所在地': loaction,
					'所在小区': all_conflg[0],
					'规格': all_conflg[1],
					'面积': all_conflg[2],
					'电梯': all_conflg[-1],
					'总价': total_price,
					'单价': unit_price,
					'查重url': url,
				}
				save_to_mongo(data)
		time.sleep(3)

# 获取所需爬取城市各地区二手房信息的url
def ready_steup(url):
	group = []
	html = request(url)
	if html:
		soup = BeautifulSoup(html, 'lxml')
	for item in soup.find('div', class_='position').find_all('dl')[1].find_all('div')[1].find_all('a'):
		area = item.text
		second_url = head_url + item['href']
		second_html = request(second_url)
		if second_html:
			second_soup = BeautifulSoup(second_html, 'lxml')
			total_room = second_soup.find('div', class_='resultDes').find('h2').find('span').text
			if int(total_room) <= 3000:
				goal_url = {
					'area': area,
					'url': second_url,
				}
				yield goal_url
			else:
				for a in second_soup.find('div', class_='position').find_all('dl')[1].find_all('div')[2].find_all('a'):
					goal_url = {
						'area': area,
						'url': head_url + a['href'],
					}
					yield goal_url

def main():
	browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
	browser.set_window_size(1400, 900)
	for url in ready_steup(entrance_url):
		print('获取地区url成功,正在获取页数')
		total_page = get_total_page(browser ,url['url'])
		if total_page:
			for page in range(1, int(total_page)+1):
				goal_url = url['url'] + 'pg' + str(page)
				if table.find_one({'查重url': goal_url}):
					print(goal_url, '已经爬取过了......')
					continue
				parse_page(url['area'], goal_url)
	print('全部页面爬取完成。')
	browser.close()

if __name__ == '__main__':
	main()
