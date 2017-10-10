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

class PilkadaJabar2018DetiknewscomSpider(BaseSpider):
    name = "pilkada_jabar_2018_detiknewscom"
    start_urls = (
        'https://pilkada.detik.com/daerah/jawa-barat',
    )

    def __init__(self):
        media_id = "detiknewscom"
        election_id = "pilkada_jabar_2018"
        super(PilkadaJabar2018DetiknewscomSpider, self).__init__(media_id, election_id)

    def parse(self, response):
        is_no_update = False

        articles = response.css("div.l_content > ul > li > article")
        if articles:
            for article in articles:
                url_selector = article.css("a::attr(href)")
                if not url_selector:
                    raise CloseSpider('url_selectors not found')
                url = url_selector.extract()[0]
                # print url

                # parse date
                date_selectors = article.css("div.box_text > div.date::text")
                if not date_selectors:
                    raise CloseSpider('url_selectors not found')
                date_str = date_selectors.extract()[0]

                # date_str = Senin, 09 Okt 2017 16:12 WIB

                info_time = date_str.split(',')[1].strip()
                time_arr = filter(None, re.split('[\s,|]',info_time))[:4]
                info_time = ' '.join([_(s) for s in time_arr if s])

                try:
                    published_at_wib = datetime.strptime(info_time, '%d %b %Y %H:%M')
                except ValueError as e:
                    raise CloseSpider('cannot_parse_date: %s' % e)

                #convert to utc+0
                published_at = wib_to_utc(published_at_wib)

                # eg: 6 Hours ago
                if self.media['last_crawl_at'] >= published_at:
                    is_no_update = True
                    break

                yield Request(url=url, callback=self.parse_news)

        if is_no_update:
            self.logger.info('Media have no update')
            return

        if response.css("div.paging_ > a.pn::attr(href)"):
            next_page = response.css("div.paging_ > a.pn::attr(href)")[1].extract()
            yield Request(next_page, callback=self.parse)

    def parse_news(self, response):

        loader = ItemLoader(item=News(), response=response)
        loader.add_value('url', response.url)

        loader.add_value('media_id', self.media_id)
        loader.add_value('election_id', self.election_id)

        #parse title
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
        date_str = date_selectors.extract()[0]

        date_str = filter(None, re.split('[\s,]', date_str))[1:5]
        info_time = ' '.join([_(s) for s in date_str if s])

        #parse date information
        try:
            published_at_wib = datetime.strptime(info_time, '%d %B %Y %H:%M')
        except ValueError as e:
            raise CloseSpider('cannot_parse_date: %s' % e)

        #convert to utc+0
        published_at = wib_to_utc(published_at_wib)
        loader.add_value('published_at', published_at)

        #TODO check the published_at, if it is smaller than the last time
        #we crawl, just drop the data.

        #parse author name
        author_name_selectors = response.css("div.detail > article > div.detail_area > div.author > strong::text")
        if not author_name_selectors:
            loader.add_value('author_name', 'N/A')
        else:
            author_name = author_name_selectors.extract_first()
            loader.add_value('author_name', author_name)

        #parse raw content
        raw_content_selectors = response.css("div.detail > article > div.text_detail.detail_area")
        if not raw_content_selectors:
            return loader.load_item()
        raw_content = raw_content_selectors.extract_first()
        loader.add_value('raw_content', raw_content)

        return loader.load_item()
