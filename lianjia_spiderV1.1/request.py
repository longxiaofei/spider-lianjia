import requests
import random
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import SERVICE_ARGS
import time

USER_LIST = [
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
	"Opera/8.0 (Windows NT 5.1; U; en)",
	"Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
	"Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11", 
	"TaoBrowser/2.0 Safari/536.11"
]

headers = {
	'User-Agent': random.choice(USER_LIST),
	'Connection': 'keep-alive',
}

def request(url):
	try:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			return response.text
		else:
			print(url, '：错误页面！......')
			time.sleep(25)
			return None
	except RequestException as e:
		print('获取', url, '失败......')
		time.sleep(25)
		return None

# 获取一个地区二手房信息的总页数
def get_total_page(browser, url):
	browser.get(url)
	try:
		time.sleep(4)
		total_room = browser.find_element_by_xpath('/html/body/div[4]/div[1]/div[2]/h2/span').text
		if not total_room:
			return None
		if int(total_room) <= 30:
			return 1
		total = WebDriverWait(browser, 30).until(
				EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[7]/div[2]/div/a[last()]"))
			)
		if not total.text.isdigit():
			total_page = browser.find_element_by_xpath('/html/body/div[4]/div[1]/div[7]/div[2]/div/a[last()-1]').text
		else:
			total_page = total.text
		return total_page
	except TimeoutException as e:
		print('获取总页数失败，25秒后重新获取')
		time.sleep(25)
		return get_total_page(url)




