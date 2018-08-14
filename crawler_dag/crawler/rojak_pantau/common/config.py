# -*- coding: utf-8 -*-
import os

def db_host():
  return os.getenv('ROJAK_DB_HOST', 'rojak-crawler-db')

def db_port():
  return int(os.getenv('ROJAK_DB_PORT', 3306))

def db_user():
  return os.getenv('ROJAK_DB_USER', 'rojak')

def db_pass():
  return os.getenv('ROJAK_DB_PASS', 'rojak')

def db_name():
  return os.getenv('ROJAK_DB_NAME', 'crawler')

def slack_token():
  return os.getenv('ROJAK_SLACK_TOKEN', '')
