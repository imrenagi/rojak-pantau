# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb as mysql
import logging
from scrapy.exceptions import CloseSpider, DropItem

class NewsValidation(object):
    def process_item(self, item, spider):
        title = item.get('title', 'title_not_set')
        if title == 'title_not_set':
            err_msg = 'Missing title in: %s' % item.get('url')
            raise DropItem(err_msg)

        raw_content = item.get('raw_content', 'raw_content_not_set')
        if raw_content == 'raw_content_not_set':
            err_msg = 'Missing raw_content in: %s' % item.get('url')
            raise DropItem(err_msg)

        published_at = item.get('published_at', 'published_at_not_set')
        if published_at == 'published_at_not_set':
            err_msg = 'Missing published_at in: %s' % item.get('url')
            raise DropItem(err_msg)

        media_id = item.get('media_id', 'media_id_empty')
        if media_id == 'media_id_empty':
            err_msg = 'Missing media id in: %s' % item.get('url')
            raise DropItem(err_msg)

        election_id = item.get('election_id', 'election_id_empty')
        if election_id == 'election_id_empty':
            err_msg = 'Missing election id in: %s' % item.get('url')
            raise DropItem(err_msg)

        # Pass item to the next pipeline, if any
        return item

class SaveToMySQL(object):
    sql_insert_news = '''
        INSERT INTO `news`(
        `media_id`,
        `election_id`,
        `title`,
        `raw_content`,
        `url`,
        `author_name`,
        `published_at`)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    '''

    def process_item(self, item, spider):
        url = item.get('url')
        title = item.get('title')
        author_name = item.get('author_name')
        raw_content = item.get('raw_content')
        published_at = item.get('published_at')
        media_id = item.get('media_id')
        election_id = item.get('election_id')

        # Insert to the database
        try:
            spider.cursor.execute(self.sql_insert_news, [media_id, election_id,
                title, raw_content, url, author_name, published_at])
            spider.db.commit()
        except mysql.Error as err:
            error_msg = '{}: Unable to save news: {} err: {}'.format(spider.name, url, err)
            logging.warning(error_msg)
            spider.db.rollback()
            if spider.is_slack:
                spider.slack.chat.post_message('#rojak-pantau-errors', error_msg, as_user=True)

        return item
