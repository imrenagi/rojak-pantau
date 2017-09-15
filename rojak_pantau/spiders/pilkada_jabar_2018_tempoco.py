# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider, DropItem

from rojak_pantau.items import News
from rojak_pantau.i18n import _
from rojak_pantau.util.wib_to_utc import wib_to_utc
from rojak_pantau.spiders.base import BaseSpider

class PilkadaJabar2018TempoSpider(BaseSpider):
    name = "pilkada_jabar_2018_tempoco"
    allowed_domains = ["tempo.co"]
    start_urls = (
        'https://m.tempo.co/topik/masalah/2461/pilkada-jawa-barat#',
    )

    def __init__(self):
        media_id = "tempoco"
        election_id = "pilkada_jabar_2018"
        super(PilkadaJabar2018TempoSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        self.logger.info('parse: %s' % response)
        is_no_update = False
        print self.media['last_crawl_at']

        #1st article
        article1 = response.css('div.block-box')
        if not article1:
            raise CloseSpider('article not found')

        url_selector = article1.css("h3.title > a::attr(href)")
        if not url_selector:
            raise CloseSpider('url_selectors not found')
        url = url_selector.extract_first()

        published_at = self.extract_date_from_url(url)
        # if self.media['last_crawl_at'] >= published_at:
        #     is_no_update = True
        #     self.logger.info('Main section is stalled')
        #     return

        yield Request(url=url, callback=self.parse_news)

        #2nd and 3rd article
        articles = response.css('div.block-box > ul.side-list > li')
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("h4 > a::attr(href)")
            if not url_selector:
                continue
                raise CloseSpider('url_selectors not found')
            url = url_selector.extract_first()

            published_at = self.extract_date_from_url(url)
            # if self.media['last_crawl_at'] >= published_at:
            #     is_no_update = True
            #     break

            yield Request(url=url, callback=self.parse_news)

        # if is_no_update:
        #     self.logger.info('Second section has no update')
        #     return

        # parse the list news
        articles = response.css('ul#ListTerkini > li')
        if not articles:
            raise CloseSpider('articles not found')

        for article in articles:
            url_selector = article.css("li > h4 > a::attr(href)")
            if not url_selector:
                continue
                raise CloseSpider('url_selectors not found')
            url = url_selector.extract_first()

            published_at = self.extract_date_from_url(url)
            # if self.media['last_crawl_at'] >= published_at:
            #     is_no_update = True
            #     break

            yield Request(url=url, callback=self.parse_news)

        # if is_no_update:
        #     self.logger.info('Reach the recent news')
        #     raise CloseSpider('Close spiders because reach the recent news')

    def extract_date_from_url(self, url):
        # date equals to '2017 01 31'
        date = ' '.join(url.split('/')[-5:-2])
        try:
            published_at_wib = datetime.strptime(date, '%Y %m %d')
        except ValueError as e:
            raise CloseSpider('cannot_parse_date: %s' % e)

        #convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        return published_at


    def parse_news(self, response):
        self.logger.info('parse_news: %s' % response)

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        #parse title
        title_selectors = response.css('div.artikel > h1.artikel::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        #parse date
        date_selectors = response.css('div.artikel > div.tanggal::text')
        if not date_selectors:
            return loader.load_item()
        date_str = date_selectors.extract_first()

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

        if self.media['last_crawl_at'] >= published_at:
            is_no_update = True
            return loader.load_item()

        loader.add_value('published_at', published_at)

        #parse author name
        author_name_selectors = response.css('div.artikel > div > p > strong::text')
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract()[-1].strip()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css('div.artikel > div > p')
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
