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
from rojak_pantau.spiders.pilkada_2018_merdekacom import Pilkada2018MerdekacomSpider

class PilkadaJatim2018MerdekacomSpider(Pilkada2018MerdekacomSpider):
    name = "pilkada_jatim_2018_merdekacom"
    start_urls = (
        'https://m.merdeka.com/tag/p/pilgub-jatim/',
    )

    def __init__(self):
        media_id = "merdekacom"
        election_id = "pilkada_jatim_2018"
        super(PilkadaJatim2018MerdekacomSpider, self).__init__(media_id, election_id)
