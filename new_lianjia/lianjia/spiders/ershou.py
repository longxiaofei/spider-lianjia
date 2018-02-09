# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from copy import deepcopy
import json
import re


class ErshouSpider(Spider):
    name = 'ershoufang'
    allowed_domains = ['lianjia.com']

    def start_requests(self):
        url = 'https://bj.lianjia.com/'
        yield Request(url=url, callback=self.get_all_city)

    def get_all_city(self, response):
        for city in response.xpath('//*[contains(@class, "fc-main")]//a'):
            city_url = city.xpath('./@href').extract_first()
            is_go = re.match(r'https://[a-z]+\.lianjia\.com/', city_url)
            if is_go:
                zufang_url = city_url + 'ershoufang/'
                yield Request(url=zufang_url, callback=self.get_all_area)

    def get_all_area(self, response):
        for area in response.xpath('//*[@id="position"]/dl[2]//a'):
            area_url = area.xpath('./@href').extract_first()
            if 'https' not in area_url and 'ershoufang' in area_url:
                head_url = response.url.replace('/ershoufang/', '')
                area_url = head_url + area_url
                yield Request(url=area_url, callback=self.get_all_detail_area)

    def get_all_detail_area(self, response):
        all_detail_area = response.xpath('//*[@id="position"]//*[contains(@class, "section_sub_sub_nav")]//a')
        for detail_area in all_detail_area:
            detail_area_url = detail_area.xpath('./@href').extract_first()
            head_url = re.sub(r'/ershoufang.*', '', response.url)
            detail_area_url = head_url + detail_area_url
            yield Request(url=detail_area_url, callback=self.parse_index)

    def parse_index(self, response):
        ljConf = response.xpath('//script[1]').extract_first()
        city = re.search(r'city_name: \'(.*?)\',', ljConf).group(1)
        area = response.xpath('//*[@id="position"]/dl[2]//*[@class="selected"]/text()').extract()[0]
        house_nums = response.xpath('//h2[contains(@class, "total")]/span/text()').extract_first().strip(' ')

        if int(house_nums):
            for house_data in response.xpath('.//*[@class="bigImgList"]//div[@class="item"]'):
                title = house_data.xpath('.//*[@class="title"]/text()').extract_first()
                link_url = house_data.xpath('.//*[@class="title"]/@href').extract_first()
                price = house_data.xpath('.//*[@class="price"]/span/text()').extract_first()
                house_info = house_data.xpath('.//*[@class="info"]//text()').extract()
                region = house_info[0]
                zone = house_info[2]
                meters = house_info[4]
                direction = house_info[6]
                house_style = house_info[8]
                try:
                    is_elevator = house_info[10]
                except:
                    is_elevator = '未知'
                labels = house_data.xpath('.//*[@class="tag"]//text()').extract()

                test = {
                    'title': title,             #标题
                    'link_url': link_url,       #链接
                    'price': price,             #价格    
                    'region': region,           #所在小区
                    'zone': zone,               #几室几厅
                    'meters': meters,           #面积
                    'direction': direction,     #方向
                    'house_style': house_style, #装修
                    'is_elevator': is_elevator, #有无电梯
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