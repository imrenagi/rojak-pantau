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

class Pilpres2019RepublikacoidSpider(BaseSpider):

    custom_settings = {"USER_AGENT":'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

    name = "pilpres_2019_republikacoid"
    start_urls = (
        'https://www.republika.co.id/indeks/hot_topic/pilpres_2019',
    )

    def __init__(self):
        media_id = "republikacoid"
        election_id = "pilpres_2019"
        super(Pilpres2019RepublikacoidSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        is_no_update = False

        articles = response.css("div.left_ib_rightx > div.set_subkanal > div.txt_subkanal")
        if articles:
            for article in articles:
                # TODO handle for photo

                url_selector = article.css("h2 > a::attr(href)")
                if not url_selector:
                    continue
                url = url_selector.extract_first()

                # parse date
                date_selectors = article.css("h6::text")
                if not date_selectors:
                    continue
                date_str = date_selectors.extract_first()

                # Tuesday, 14 Aug 2018 21:37 WIB

                info_time = date_str.split(',')[1].strip()
                time_arr = filter(None, re.split('[\s,|]', info_time))[:4]
                info_time = ' '.join([_(s) for s in time_arr if s])

                print url
                print date_str

                try:
                    published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
                except ValueError as e:
                    raise CloseSpider('cannot_parse_date: %s in %s' % (e, url))

                # convert to utc+0
                published_at = wib_to_utc(published_at_wib)

                # TODO
                if self.media['last_crawl_at'] >= published_at:
                    is_no_update = True
                    continue

                yield Request(url=url, callback=self.parse_news)

        if response.css("div.pagination > section > nav > a"):
            links = response.css("div.pagination > section > nav > a")
            for link in links:
                l = link.css("a::text").extract_first()
                if l.lower() == 'next':
                    next_page = link.css("a::attr(href)").extract_first()
                    print next_page
                    yield Request(next_page, callback=self.parse)
                else:
                    continue

    def parse_news(self, response):

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        # parse title
        title_selectors = response.css('div.wrap_detail > div.wrap_detail_set > h1::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        # parse date
        date_selectors = response.css("div.wrap_detail > div.wrap_detail_set > div.date_detail > p::text")
        if not date_selectors:
            return loader.load_item()

        # Senin 13 Agustus 2018 19:43 WIB

        date_str = date_selectors.extract_first()
        date_str = re.sub('\s+', ' ', date_str)
        date_str = filter(None, re.split('[\s,]', date_str))[1:5]
        info_time = ' '.join([_(s) for s in date_str if s])

        # parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
        except ValueError as e:
            raise CloseSpider('cannot_parse_date: %s in %s' % (e, response.url))

        # convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        loader.add_value('published_at', published_at)

        # TODO check the published_at, if it is smaller than the last time
        # we crawl, just drop the data.

        # parse author name
        author_name_selectors = response.css("div.wrap_detail > div.wrap_detail_set > div.by > span > p::text")
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract_first()
            author_name = re.sub('\s+', ' ', author_name)
            loader.add_value('author_name', author_name)

        # parse raw content
        raw_content_selectors = response.css("div.set_conten_detail > div.detail_img_set > div.teaser_detail > div.artikel")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
