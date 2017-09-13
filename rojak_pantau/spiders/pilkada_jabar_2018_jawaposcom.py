# -*- coding: utf-8 -*-
import scrapy
import re
from dateparser import parse
from datetime import datetime
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider

from rojak_pantau.items import News
from rojak_pantau.i18n import _
from rojak_pantau.util.wib_to_utc import wib_to_utc
from rojak_pantau.spiders.base import BaseSpider

class OldNewsException(Exception):
    pass

class PilkadaJabar2018JawaposSpider(scrapy.Spider):
    name = "pilkada_jabar_2018_jawaposcom"
    start_urls = (
        'https://www.jawapos.com/tag/15041/pilgub-jabar',
    )

    def parse(self, response):
        base_url = "https://m.jawapos.com"

        articles = response.css("div.wrp-itemnewsterkini > div.item-newsterkini")
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("a::attr(href)")
            if not url_selector:
                raise CloseSpider('url_selectors not found')
            url = url_selector.extract()[0]

            # parse date
            date_selectors = response.css("div.date-tag::text")
            if not date_selectors:
                raise CloseSpider('url_selectors not found')
            date_str = date_selectors.extract()[0]

            # eg: 6 Hours ago
            date_str = date_str.split("|")[0].strip()
            time_in_utc = parse(date_str)

            #TODO check the last time for scrapping

            yield Request(url=url, callback=self.parse_news)

        if response.css('a[rel="next"]::attr(href)'):
            next_page = response.css('a[rel="next"]::attr(href)')[0].extract()
            yield Request(next_page, callback=self.parse)

    def parse_news(self, response):
        self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        #parse title
        title_selectors = response.css('h1::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        # parse date
        date_selectors = response.css("div.date > span::text")
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract()[0]

        # eg: Selasa, 12 Sep 2017 20:08
        date_str = date_str.split(",")[1].strip()
        time_arr = filter(None, re.split('[\s,|]',date_str))
        info_time = ' '.join([_(s) for s in time_arr if s])

        #parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d %b %Y %H:%M')
        except ValueError as e:
            raise CloseSpider('cannot_parse_date: %s' % e)

        #convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        loader.add_value('published_at', published_at)

        #TODO check the published_at, if it is smaller than the last time
        #we crawl, just drop the data.

        #parse author name
        author_name_selectors = response.css("div.date > span")[1].css("span > span::text")
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract_first()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css("div.contentdetail")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
