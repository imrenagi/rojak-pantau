# -*- coding: utf-8 -*-
import scrapy
import MySQLdb as mysql
import os
from datetime import datetime
from slacker import Slacker

from scrapy.exceptions import CloseSpider, NotConfigured
from scrapy import signals

from rojak_pantau.common import config, sql

class BaseSpider(scrapy.Spider):
    # Initialize database connection then retrieve media ID and
    # last_scraped_at information
    def __init__(self, media_id, election_id):
        # Open database connection
        self.db = mysql.connect(
            host=config.db_host(),
            port=config.db_port(), 
            user=config.db_user(),
            passwd=config.db_pass(),
            db=config.db_name()
        )
        self.cursor = self.db.cursor()

        self.media = {}
        self.media_id = media_id
        self.election_id = election_id

        try:
            # Get media information from the database
            self.logger.info('Fetching media information')
            self.cursor.execute(sql.get_media(), [self.media_id, self.election_id])
            row = self.cursor.fetchone()
            self.media['id'] = row[0]
            self.media['last_crawl_at'] = row[1]
        except mysql.Error as err:
            self.logger.error('Unable to fetch media data: %s', err)
            raise NotConfigured('Unable to fetch media data: %s' % err)

        if config.slack_token() != '':
            self.is_slack = True
            self.slack = Slacker(config.slack_token())
        else:
            self.is_slack = False
            self.logger.info('Post error to #rojak-pantau-errors is disabled')

    # Capture the signal spider_opened and spider_closed
    # https://doc.scrapy.org/en/latest/topics/signals.html
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler,
                *args, **kwargs)
        crawler.signals.connect(spider.spider_opened,
                signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed,
                signal=signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        # Using UTF-8 Encoding
        self.db.set_character_set('utf8')
        self.cursor.execute('SET NAMES utf8mb4;')
        self.cursor.execute('SET CHARACTER SET utf8mb4;')
        self.cursor.execute('SET character_set_connection=utf8mb4;')

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s %s', spider.name, reason)
        # if spider finished without error update last_scraped_at
        if reason == 'finished':
            try:
                self.logger.info('Updating media last_scraped_at information')
                self.cursor.execute(sql.update_media(), [spider.media_id, spider.election_id])
                self.db.commit()
                self.db.close()
            except mysql.Error as err:
                self.logger.error('Unable to update last_scraped_at: %s', err)
                self.db.rollback()
                self.db.close()
                if self.is_slack:
                    error_msg = '{}: Unable to update last_scraped_at: {}'.format(
                        spider.name, err)
                    self.slack.chat.post_message('#rojak-pantau-errors', error_msg,
                        as_user=True)
        else:
            if self.is_slack:
                # Send error to slack
                error_msg = '{}: Spider fail because: {}'.format(
                    spider.name, reason)
                self.slack.chat.post_message('#rojak-pantau-errors',
                        error_msg, as_user=True)

    # subscibe to item_droped event
    def item_dropped(self, item, response, exception, spider):
        if self.is_slack:
            # Send error to slack
            error_msg = '{}: Item dropped because: {}'.format(
                spider.name, exception)
            spider.slack.chat.post_message('#rojak-pantau-errors',
                    error_msg, as_user=True)

    # parse is to be implemented by concrete class
    # for parsing the list of news articles
    def parse(self, response):
        pass

    # parse_news is to be implemented by concrete class
    # for parsing each of article news
    def parse_news(self, response):
        pass
