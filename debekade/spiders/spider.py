import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import DebekadeItem
from itemloaders.processors import TakeFirst


class DebekadeSpider(scrapy.Spider):
	name = 'debekade'
	start_urls = ['https://www.debeka.de/unternehmen/presse/aktuelle-meldungen/2021/index.html']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news"]//a[@class="aContentNone"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@id="moreInformation"]//a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h2/text()').get()
		description = response.xpath('//div[@id="newsContent"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@id="publication"]/text()').get()
		if date:
			date = re.findall(r'\d{2}\.\d{2}\.\d{4}', date)[0]

		item = ItemLoader(item=DebekadeItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
