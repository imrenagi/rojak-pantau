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

class Pilpres2019TribunnewsSpider(BaseSpider):

    name = "pilpres_2019_pikiranrakyat"
    start_urls = (
        'http://m.tribunnews.com/topic/pilpres-2019',
    )

    def __init__(self):
        media_id = "pikiranrakyat"
        election_id = "pilpres_2019"
        super(Pilpres2019TribunnewsSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        is_no_update = False

        articles = response.css("div.view-content > div > article")

        if articles:
            for article in articles:
                url_selector = article.css("div.entry-main > h2.entry-title > a ::attr(href)")
                if not url_selector:
                    continue
                url = url_selector.extract_first()

                info_selectors = article.css("div.entry-main > div.entry-meta > span.entry-date > span::text")
                if not info_selectors:
                    continue

                # 25 July, 2018 - 11:04
                info = info_selectors.extract_first()

                info_time = re.sub(r'[,-]', '', info)
                info_time = re.sub(r'\s+', ' ', info_time)
                time_arr = filter(None, re.split('[\s,|-]', info_time))[:4]
                info_time = ' '.join([_(s) for s in time_arr if s])

                #parse date information
                try:
                    published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
                except ValueError as e:
                    raise CloseSpider('cannot_parse_date: %s' % e)

                #convert to utc+0
                published_at = wib_to_utc(published_at_wib)

                if self.media['last_crawl_at'] >= published_at:
                    is_no_update = True
                    break

                print url
                print published_at_wib

                yield Request(url=url, callback=self.parse_news)

        if is_no_update:
            self.logger.info('Media have no update')
            return

        next_selectors = response.css("div.ma10.paging#paginga > a")
        for num in range(0,len(next_selectors)):
            if next_selectors[num].css("a::text").extract_first().lower() == 'next':
                next_url = next_selectors[num].css("a::attr(href)").extract_first()
                yield Request(next_url, callback=self.parse)
                break

    def parse_news(self, response):

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        #parse title
        title_selectors = response.css('div.main-container > div > section.main-content > h1.page-header::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        #parse date
        date_selectors = response.css('div.post-meta > div > div > div.submitted > span::text')
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract_first()
        info_time = re.sub(r'[,-]', '', date_str)
        info_time = re.sub(r'\s+', ' ', info_time)
        time_arr = filter(None, re.split('[\s,|-]', info_time))[:4]
        info_time = ' '.join([_(s) for s in time_arr if s])

        #parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
        except ValueError as e:
            return loader.load_item()

        #convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        loader.add_value('published_at', published_at)

        #parse author name
        author_name_selectors = response.css('div.post-meta > div > div > div.items-penulis > span > a::text').extract_first()
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css('div.region.region-content > section > article > div.field.field-name-body.field-type-text-with-summary > div.field-items > div.field-item.even')
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
