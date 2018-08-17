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

class Pilpres2019DetiknewscomSpider(BaseSpider):
    name = "pilpres_2019_detiknewscom"
    start_urls = (
        'https://www.detik.com/tag/pilpres-2019',
    )

    def __init__(self):
        media_id = "detiknewscom"
        election_id = "pilpres_2019"
        super(Pilpres2019DetiknewscomSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        is_no_update = False

        articles = response.css("div.list.media_rows.list-berita > article")
        if articles:
            for article in articles:
                # TODO handle for photo

                url_selector = article.css("a::attr(href)")
                if not url_selector:
                    continue

                url = url_selector.extract_first()
                print url

                # parse date
                date_selectors = article.css("a > span.box_text > span.date::text")
                if not date_selectors:
                    continue
                date_str = date_selectors.extract_first()

                # date_str = Senin, 09 Okt 2017 16:12 WIB

                info_time = date_str.split(',')[1].strip()
                time_arr = filter(None, re.split('[\s,|]', info_time))[:4]
                info_time = ' '.join([_(s) for s in time_arr if s])

                try:
                    published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
                except ValueError as e:
                    raise CloseSpider('cannot_parse_date: %s in %s' % (e, url))

                # convert to utc+0
                published_at = wib_to_utc(published_at_wib)

                # TODO
                # eg: 6 Hours ago
                if self.media['last_crawl_at'] >= published_at:
                    is_no_update = True
                    break

                yield Request(url=url, callback=self.parse_news)

        # if is_no_update:
        #     self.logger.info('Media have no update')
        #     return

        if response.css("div.paging.text_center > a.last"):
            navs = response.css("div.paging.text_center > a.last")
            for nav in navs:
                direction = nav.css("img::attr(alt)").extract_first()
                if direction.lower() == 'kanan':
                    next_page = nav.css("a::attr(href)").extract_first()

                    yield Request(next_page, callback=self.parse)

    def parse_news(self, response):

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        # parse title
        title_selectors = response.css('div.detail > article > div.detail_area > h1::text')
        if not title_selectors:
            return loader.load_item()
        title = title_selectors.extract_first()
        loader.add_value('title', title)

        # parse date
        date_selectors = response.css("div.detail > article > div.detail_area > div.date::text")
        if not date_selectors:
            return loader.load_item()
        # Selasa 10 Oktober 2017, 13:40 WIB
        date_str = date_selectors.extract_first()

        date_str = filter(None, re.split('[\s,]', date_str))[1:5]
        info_time = ' '.join([_(s) for s in date_str if s])

        # parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
        except ValueError as e:
            return loader.load_item()

        # convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        loader.add_value('published_at', published_at)

        # TODO check the published_at, if it is smaller than the last time
        # we crawl, just drop the data.

        # parse author name
        author_name_selectors = response.css("div.detail > article > div.detail_area > div.author > strong::text")
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract_first()
            loader.add_value('author_name', author_name)

        # parse raw content
        raw_content_selectors = response.css("div.detail > article > div.text_detail.detail_area")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
