# rojak-pantau

We are using [Scrapy](https://doc.scrapy.org) as the base for `rojak-pantau`.
The reason of using this crawling framework are discussed below:

1. Fit the team needs. Any person who would like to add a new crawler for a media only need to add small changes to the source code.
2. Easy to deploy
3. Good at documentation

## Setup
Make sure you have MySQL and its table ready. To populate the table use this following commands:
```
cd rojak-database
python insert_candidate_data.py
python insert_media_data.py
```

## Run the crawler
```
sh install_dependencies.sh
scrapy crawl detikcom # change detikcom with the crawler name
```

## Adding new media crawler

To add new media crawler, copy `rojak_pantau/spider/detikcom.py`
and change the file name to the name of the media. Then, modify `name`, `start_urls`, `parse` method and `parse_news` method.

## Notes for writing new crawler

* crawler name must follow this following format: `<pilpres/pilkada>_<indo/province_name>_<year>_<mediaid>.py`. For instance:
```
pilpres_indo_2019_kompascom.py
pilkada_jabar_2018_merdekacom.py
```

* `raw_content` must contains the raw HTML text, not the raw plain text, since this information is gonna be used for specific text processing. (e.g. extracting the first paragraph)

## Resources

* [Scrapy 1.2 documentation](https://doc.scrapy.org/en/latest/index.html)
