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

class PilkadaJabar2018PikiranRakyatSpider(BaseSpider):
    name = "pilkada_jabar_2018_pikiranrakyatcom"
    allowed_domains = ["pikiran-rakyat.com"]
    start_urls = (
        'http://www.pikiran-rakyat.com/tags/pilgub-jabar',
    )

    def __init__(self):
        media_id = "pikiranrakyatcom"
        election_id = "pilkada_jabar_2018"
        super(PilkadaJabar2018PikiranRakyatSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        base_url = "http://www.pikiran-rakyat.com"
        self.logger.info('parse: %s' % response)

        articles = response.css("div.view-content > div")
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("h2.entry-title > a::attr(href)")
            if not url_selector:
                continue
                raise CloseSpider('url_selectors not found')
            url = base_url + url_selector.extract()[0]

            info_selectors = article.css("div.entry-meta > span.entry-date > span::text")
            if not info_selectors:
                raise CloseSpider('info_selectors not found')
            #info = 12 September, 2017 - 15:15
            info = info_selectors.extract_first()

            time_arr = filter(None, re.split('[\s,-]',info))
            info_time = ' '.join([_(s) for s in time_arr if s])

            #parse date information
            try:
                published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
            except ValueError as e:
                raise CloseSpider('cannot_parse_date: %s' % e)

            #convert to utc+0
            published_at = wib_to_utc(published_at_wib)

            # #TODO check the last time for scrapping
            #

            yield Request(url=url, callback=self.parse_news)

        pagination = response.css('div.text-center > ul.pagination > li.next')
        if pagination:
            next_page = base_url+pagination.css('a::attr(href)').extract_first()
            yield Request(next_page, callback=self.parse)

    def parse_news(self, response):
        self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        #parse title
        title_selectors = response.css('section.main-content > h1::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        #parse date
        date_selectors = response.css("div.submitted > span::text")
        if not date_selectors:
            return loader.load_item()
        # eg: 5 September, 2017 - 18:54
        date_str = date_selectors.extract_first()

        time_arr = filter(None, re.split('[\s,-]',date_str))
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
            author_name = author_name_selectors.extract()[0].strip()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css("div.field-item.even")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
