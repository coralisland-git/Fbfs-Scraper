# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from lxml import etree

from lxml import html

import pdb



class fbfs(scrapy.Spider):

	name = 'fbfs'

	domain = 'https://www.fbfs.com/'

	history = []


	def start_requests(self):

		url = 'https://www.fbfs.com/landing-page/agent-listing'

		yield scrapy.Request(url, callback=self.parse)


	def parse(self, response):

		person_list = response.xpath('//div[@class="linkContainer"]//a/@href').extract()

		for person in person_list:

			loc_link = person + '/Locations'

			info_link = person + '/MeetMe'

			yield scrapy.Request(loc_link, callback=self.parse_detail, meta={ 'info_link' : info_link, 'origin_link' : person })


	def parse_detail(self, response):

		item = ChainItem()

		location = response.xpath('//ul[@class="office-locations"]//li[@class="office-location"][1]')

		item['address'] = ''.join(location.xpath('.//span[@itemprop="streetAddress"]//text()').extract()).strip()

		item['city'] = ''.join(location.xpath('.//span[@itemprop="addressLocality"]//text()').extract()).strip()

		item['state'] = ''.join(location.xpath('.//span[@itemprop="addressRegion"]//text()').extract()).strip()

		item['zipcode'] = ''.join(location.xpath('.//span[@itemprop="postalCode"]//text()').extract()).strip()

		item['link'] = response.meta['origin_link']

		yield scrapy.Request(response.meta['info_link'], callback=self.parse_info, meta={ 'item' : item })


	def parse_info(self, response):

		item = response.meta['item']

		item['name'] = ''.join(response.xpath('//h2[@itemprop="name"]//text()').extract()).strip()

		detail = response.xpath('//figcaption[@class="agent-meet-me-contact-info"]')

		item['info'] = ''.join(detail.xpath('.//li[@itemscope="itemscope"]//text()').extract()).strip()

		item['phone'] = ''.join(detail.xpath('.//a[@itemprop="telephone"]//text()').extract()).strip()

		item['email'] = ''.join(detail.xpath('.//a[@itemprop="email"]//text()').extract()).strip()

		yield item


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp