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
from rojak_pantau.spiders.pilkada_2018_detiknewscom import Pilkada2018DetiknewscomSpider

class PilkadaJatim2018DetiknewscomSpider(Pilkada2018DetiknewscomSpider):
    name = "pilkada_jatim_2018_detiknewscom"
    start_urls = (
        'https://pilkada.detik.com/daerah/jawa-timur',
    )

    def __init__(self):
        media_id = "detiknewscom"
        election_id = "pilkada_jatim_2018"
        super(PilkadaJatim2018DetiknewscomSpider, self).__init__(media_id, election_id)
