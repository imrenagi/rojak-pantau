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

class PilkadaJabar2018RepublikaSpider(scrapy.Spider):
    name = "pilkada_jabar_2018_republika"
    allowed_domains = ["republika.co.id"]
    start_urls = (
        'http://m.republika.co.id/indeks/hot_topic/pilkada_jabar',
    )

    def parse(self, response):
        # self.logger.info('parse this url: %s' % response.url)

        articles = response.css('div.wp-terhangat')
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css('div.item3 > a::attr(href)')
            if not url_selector:
                continue
                # raise CloseSpider('url_selectors not found ' + response.url)
            url = url_selector.extract()[0]
            print url

            info_selectors = article.css("div.item3 > span::text")
            if not info_selectors:
                raise CloseSpider('info_selectors not found')
            #info = Tuesday, 12 September 2017
            info = info_selectors.extract_first()

            #info_time = 8 September 2017 16:45:19
            info_time = info.split(',')[1].strip()
            time_arr = filter(None, re.split('[\s,|]',info_time))
            info_time = ' '.join([_(s) for s in time_arr if s])

            #parse date information
            try:
                published_at_wib = datetime.strptime(info_time, '%d %B %Y')
            except ValueError as e:
                raise CloseSpider('cannot_parse_date: %s' % e)

            #convert to utc+0
            published_at = wib_to_utc(published_at_wib)
            print published_at

            #TODO check the last time for scrapping

            yield Request(url=url, callback=self.parse_news)

        if response.css('div.pagination > section > nav > ul > li.button'):
            next_page = response.css('div.pagination > section > nav > ul > li.button > a::attr(href)')[0].extract()
            yield Request(next_page, callback=self.parse)

    def parse_news(self, response):

        # self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        #parse title
        title_selectors = response.css('div.wrap-head > h2 > a::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        ##parse date
        date_selectors = response.css('div.wrap-head > span::text')
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract()[0]

        # eg: Tuesday, 12 September 2017 | 20:21 WIB
        time_arr = filter(None,re.split('[\s,|]', date_str))[1:-1]
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
        author_name_selectors = response.css('div.red::text')
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract()[0].strip()
            author_name = author_name.replace('Rep: ', '').replace('Red: ', '').strip()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css('div.content-detail')
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
