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

class PilkadaJabar2018PikiranRakyatSpider(scrapy.Spider):
    name = "pilkada_jabar_2018_pikiranrakyatcom"
    allowed_domains = ["pikiran-rakyat.com"]
    start_urls = (
        'http://www.pikiran-rakyat.com/tags/pilgub-jabar',
    )

    def parse(self, response):
        base_url = "http://www.pikiran-rakyat.com"
        self.logger.info('parse: %s' % response)

        articles = response.css("article.node-article")
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("h2.entry-title > a::attr(href)")
            if not url_selector:
                raise CloseSpider('url_selectors not found')
            url = base_url + url_selector.extract()[0]
            print url

            info_selectors = article.css("span.entry-date > span::text")
            if not info_selectors:
                raise CloseSpider('info_selectors not found')
            #info = Jumat, 8 September 2017 16:45:19
            info = info_selectors.extract_first().replace(u'\xa0',u'')

            #info_time = 8 September 2017 16:45:19
            info_time = info.split(',')[1].strip()
            time_arr = filter(None, re.split('[\s,|]',info_time))
            info_time = ' '.join([_(s) for s in time_arr if s])
            print info_time

            #parse date information
            try:
                published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M:%S')
            except ValueError as e:
                raise CloseSpider('cannot_parse_date: %s' % e)

            #convert to utc+0
            published_at = wib_to_utc(published_at_wib)

            #TODO check the last time for scrapping

            #TODO check next page in pagination
            if response.css('div.paging-box'):
                next_page = response.css('a.link_next::attr(href)').extract_first()
                next_page = response.urljoin(next_page)
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
        date_selectors = response.css("div.submitted > span::text")
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract()[0]

        # eg: 8 September 2017 21:02
        date_str = date_str.split("|")[1].strip()
        time_arr = filter(None, re.split('[\s,|]',date_str))
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
        author_name_selectors = response.css("div.items-penulis > span > a::text")
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract()[1]
            author_name = author_name.split(":")[1].strip()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css("article.node-article > div.field.field-name-body > div.field-items > div.field-item")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
