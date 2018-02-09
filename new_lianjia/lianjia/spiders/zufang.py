# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from copy import deepcopy
import json
import re


class ZufangSpider(Spider):
    name = 'zufang'
    allowed_domains = ['lianjia.com']

    def start_requests(self):
        url = 'https://bj.lianjia.com/'
        yield Request(url=url, callback=self.get_all_city)

    def get_all_city(self, response):
        for city in response.xpath('//*[contains(@class, "fc-main")]//a'):
            city_url = city.xpath('./@href').extract_first()
            is_go = re.match(r'https://[a-z]+\.lianjia\.com/', city_url)
            if is_go:
                zufang_url = city_url + 'zufang/'
                yield Request(url=zufang_url, callback=self.get_all_area)

    def get_all_area(self, response):
        for area in response.xpath('//*[@id="filter-options"]/dl[1]//a'):
            area_url = area.xpath('./@href').extract_first()
            if 'https' not in area_url:
                head_url = response.url.replace('/zufang/', '')
                area_url = head_url + area_url
                yield Request(url=area_url, callback=self.parse_index)

    def parse_index(self, response):
        ljConf = response.xpath('//script[1]').extract_first()
        city = re.search(r'city_name: \'(.*?)\',', ljConf).group(1)
        area = response.xpath('//*[@id="filter-options"]/dl[1]//div[1]//*[@class="on"]/text()').extract_first()
        house_nums = response.xpath('//*[contains(@class, "list-head")]/h2/span/text()').extract_first()

        if int(house_nums):
            for house_data in response.xpath('.//*[@id="house-lst"]//li'):
                title = house_data.xpath('.//h2/a/text()').extract_first()
                link_url = house_data.xpath('.//h2/a/@href').extract_first()
                price = house_data.xpath('.//*[@class="price"]/span/text()').extract_first()
                region = house_data.xpath('.//*[@class="region"]/text()').extract_first().replace('\xa0', '')
                zone = house_data.xpath('.//*[@class="zone"]//text()').extract_first().replace('\xa0', '')
                meters = house_data.xpath('.//*[@class="meters"]/text()').extract_first().replace('\xa0', '')
                direction = house_data.xpath('.//*[@class="where"]/span[last()]/text()').extract_first()
                other_datas = ''.join(house_data.xpath('.//*[@class="con"]//text()').extract()).split('/')
                labels = house_data.xpath('.//*[@class="chanquan"]//text()').extract()

                test = {
                    'title': title,             #标题
                    'link_url': link_url,       #链接
                    'price': price,             #价格    
                    'region': region,           #所在小区
                    'zone': zone,               #几室几厅
                    'meters': meters,           #面积
                    'direction': direction,     #方向
                    'other_datas': other_datas, #其他信息
                    'labels': labels,           #标签
                    'city': city,               #所在城市
                    'area': area,               #所在区域
                }
                print(test)

            #是否翻页
            page_datas = response.xpath('//*[contains(@class, "page-box")]/@page-data').extract_first()
            page_datas = json.loads(page_datas)
            total_page = page_datas['totalPage']
            cur_page = page_datas['curPage']
            if cur_page < total_page:
                next_page = cur_page + 1
                head_url = re.sub(r'pg\d+/', '', response.url)
                next_page_url = head_url + 'pg' + str(next_page)
                yield Request(url=area_url, callback=self.parse_index)