# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider

from rojak_pantau.items import News
from rojak_pantau.i18n import _
from rojak_pantau.util.wib_to_utc import wib_to_utc
from rojak_pantau.spiders.base import BaseSpider

class PilkadaJabar2018SindonewscomSpider(scrapy.Spider):
    name = "pilkada_jabar_2018_sindonewscom"
    allowed_domains = ["sindonews.com"]
    start_urls = (
        'https://daerah.sindonews.com/topic/673/pilgub-jabar/',
    )

    def parse(self, response):
        # self.logger.info('parse this url: %s' % response.url)

        articles = response.css('div.news > ul > li')
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css('div.breaking-title > a::attr(href)')
            if not url_selector:
                continue
                # raise CloseSpider('url_selectors not found ' + response.url)
            url = url_selector.extract()[0]
            print url

            try:
                timestamp = url.split("-")[-1]
                published_at = datetime.fromtimestamp(float(timestamp))
            except:
                continue

            #TODO check the last time for scrapping

            yield Request(url=url, callback=self.parse_news)

        pages = response.css('div.mpaging > ul > li')
        if pages:
            for page in pages:
                page_selector = page.css('a > i.fa-angle-right')
                if page_selector:
                    next_page = page.css('a::attr(href)')[0].extract()
                    yield Request(next_page, callback=self.parse)

    def parse_news(self, response):

        # self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        #parse title
        title_selectors = response.css('div.article-box > h1::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        ##parse date
        date_selectors = response.css('div.time::text')
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract()[0]

        # eg: Rabu 13 September 2017 - 12:12 WIB
        time_arr = filter(None,re.split('[\s-]', date_str))[1:-1]
        info_time = ' '.join([_(s) for s in time_arr if s])

        #parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
        except ValueError as e:
            raise CloseSpider('cannot_parse_date: %s' % e)

        #convert to utc+0
        published_at = wib_to_utc(published_at_wib)

        loader.add_value('published_at', published_at)

        #parse author name
        author_name_selectors = response.css('div.reporter > a::text')
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract()[0].strip()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css('div.content')
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
