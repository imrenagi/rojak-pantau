# -*- coding: utf-8 -*-

def get_media():
  return '''
    SELECT id,last_crawl_at FROM `crawler_history`
    WHERE media_id=%s AND election_id=%s;
  '''

def update_media():
  return '''
    UPDATE `crawler_history`
    SET last_crawl_at=UTC_TIMESTAMP()
    WHERE media_id=%s AND election_id=%s;
  '''
