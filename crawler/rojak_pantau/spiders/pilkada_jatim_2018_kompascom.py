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

    def __init__(self):
        media_id = "kompascom"
        election_id = "pilkada_jatim_2018"
        super(PilkadaJatim2018KompascomSpider, self).__init__(media_id, election_id)
