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

class PilkadaJabar2018KompasSpider(scrapy.Spider):
    name = "pilkada_jabar_2018_kompascom"
    allowed_domains = ["kompas.com"]
    start_urls = (
        'http://indeks.kompas.com/tag/Pilkada-Jabar-2018/desc/1',
    )

    def parse(self, response):
        pagination = response.url
        base_url = "http://kompas.com"
        self.logger.info('parse: %s' % response)

        articles = response.css("ul#latest_content > li.box-shadow-new")
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("h3 > a::attr(href)")
            if not url_selector:
                continue
                raise CloseSpider('url_selectors not found')
            url = url_selector.extract_first()

            # info_selectors = article.css("div.article__list__info > div.article__date::text")
            # if not info_selectors:
            #     continue
            #     raise CloseSpider('info_selectors not found')
            # #info = 12 September, 2017 - 15:15
            # info = info_selectors.extract_first()
            #
            # time_arr = filter(None, re.split('[\s,-]',info))
            # info_time = ' '.join([_(s) for s in time_arr if s])
            #
            # #parse date information
            # try:
            #     published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
            # except ValueError as e:
            #     raise CloseSpider('cannot_parse_date: %s' % e)
            #
            # #convert to utc+0
            # published_at = wib_to_utc(published_at_wib)

            # #TODO check the last time for scrapping
            #

            yield Request(url=url, callback=self.parse_news)

        next_page = pagination
        index = int(next_page.rsplit('/', 1)[-1]) + 1
        next_page = next_page.rsplit('/', 1)[-2] + "/" + str(index)
        yield Request(next_page, callback=self.parse)

    def parse_news(self, response):
        self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        #parse title
        title_selectors = response.css('h1.read__title::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        #parse date
        date_selectors = response.css('div.read__date::text')
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
        author_name_selectors = response.css('div.contentArticle.box-shadow-new > h6::text').extract_first()
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css('div.contentArticle.box-shadow-new').extract()
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
