# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider

from rojak_pantau.items import News
from rojak_pantau.util.wib_to_utc import wib_to_utc
from rojak_pantau.spiders.base import BaseSpider

class PilkadaJabar2018MerdekacomSpider(scrapy.Spider):
    name = "pilkada_jabar_2018_merdekacom"
    allowed_domains = ["m.merdeka.com"]
    start_urls = (
        'https://m.merdeka.com/tag/p/pilgub-jabar/',
    )

    def parse(self, response):
        base_url = "https://m.merdeka.com"
        self.logger.info('parse: %s' % response)

        articles = response.css("div#mdk-tag-news-list_mobile > ul > li")
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("div > a::attr(href)")
            if not url_selector:
                raise CloseSpider('url_selectors not found')
            url = base_url + url_selector.extract()[0]
            print url

            info_selectors = article.css("div > b.mdk-time::text")
            if not info_selectors:
                raise CloseSpider('info_selectors not found')
            #info = Jumat, 8 September 2017 16:45:19
            info = info_selectors.extract_first().replace(u'\xa0',u'')

            #info_time = 8 September 2017 16:45:19
            info_time = info.split(',')[1].strip()
            print info_time

            #parse date information
            #try:
                #TODO change this

            #except ValueError as e:
            #    raise CloseSpider('cannot_parse_date: %s' % e)

            #TODO convert time to UTC+0

            #TODO check the last time for scrapping

            #TODO check next page in pagination
            if response.css('div.paging-box'):
                next_page = response.css('a.link_next::attr(href)')[0].extract()
                yield Request(next_page, callback=self.parse)

            yield Request(url=url, callback=self.parse_news)

    def parse_news(self, response):
        self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        #parse title
        title_selectors = response.css('div#mdk-news-title::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        #parse date
        date_selectors = response.css("div.mdk-date-reporter > span::text")
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract()[0]

        # eg: 8 September 2017 21:02
        date_str = date_str.split("|")[1].strip()

        # try:
        #     published_at_wib = datetime.strptime(date_str, '%d %b %Y, %H:%M')
        # except ValueError:
        #     # Will be dropped on the item pipeline
        #     return loader.load_item()
        # published_at = wib_to_utc(published_at_wib)
        #TODO change this with UTC time
        loader.add_value('published_at', date_str)

        #parse author name
        author_name_selectors = response.css("div.mdk-date-reporter > span::text")
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract()[1]
            author_name = author_name.split(":")[1].strip()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css("div.mdk-body-paragraph")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
