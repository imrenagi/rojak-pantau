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
from rojak_pantau.spiders.pilkada_2018_kompascom import Pilkada2018KompascomSpider

class PilkadaJatim2018KompascomSpider(Pilkada2018KompascomSpider):
    name = "pilkada_jatim_2018_kompascom"
    start_urls = (
        'http://indeks.kompas.com/tag/Pilkada-Jatim-2018/desc/1',
    )

    custom_settings = {"USER_AGENT":'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

    def __init__(self):
        media_id = "kompascom"
        election_id = "pilkada_jatim_2018"
        super(PilkadaJatim2018KompascomSpider, self).__init__(media_id, election_id)
