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

class Pilpres2019KompascomSpider(BaseSpider):

    custom_settings = {"USER_AGENT":'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

    name = "pilpres_2019_kompascom"
    start_urls = (
        'https://indeks.kompas.com/tag/pemilu-2019/desc/',
    )

    def __init__(self):
        media_id = "kompascom"
        election_id = "pilpres_2019"
        super(Pilpres2019KompascomSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        is_no_update = False

        articles = response.css("div.article__list.clearfix")

        if articles:
            for article in articles:
                url_selector = article.css("div.article__list__title > h3 > a::attr(href)")
                if not url_selector:
                    continue
                url = url_selector.extract_first()

                info_selectors = article.css("div.article__list__info > div.article__date::text")
                if not info_selectors:
                    continue

                #info = 10/10/2017, 13:37 WIB
                info = info_selectors.extract_first()

                time_arr = filter(None,re.split('[\s,]', info))[:2]
                info_time = ' '.join([s for s in time_arr if s])
                # print info_time
                #parse date information
                try:
                    published_at_wib = datetime.strptime(info_time, '%d/%m/%Y %H:%M')
                except ValueError as e:
                    raise CloseSpider('cannot_parse_date: %s' % e)

                #convert to utc+0
                published_at = wib_to_utc(published_at_wib)

                if self.media['last_crawl_at'] >= published_at:
                    is_no_update = True
                    break

                yield Request(url=url, callback=self.parse_news)

        # if is_no_update:
        #     self.logger.info('Media have no update')
        #     return

        next_selectors = response.css("div.paging__wrap > div.paging__item > a.paging__link.paging__link--next")
        for num in range(0,len(next_selectors)):
            if next_selectors[num].css("a::attr(rel)").extract_first() == 'next':
                next_url = next_selectors[num].css("a::attr(href)").extract_first()
                yield Request(next_url, callback=self.parse)
                break

    def parse_news(self, response):

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        #parse title
        title_selectors = response.css('h1.read__title::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        #parse date
        date_selectors = response.css('div.read__time::text')
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract_first()
        # eg: Kompas.com - 10/10/2017, 13:37 WIB
        time_arr = filter(None,re.split('[\s,-]', date_str))[1:3]
        info_time = ' '.join([_(s) for s in time_arr if s])

        #parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d/%m/%Y %H:%M')
        except ValueError as e:
            return loader.load_item()

        #convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        loader.add_value('published_at', published_at)

        #parse author name
        author_name_selectors = response.css('div.read__author > a::text').extract_first()
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css('div.read__content')
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
