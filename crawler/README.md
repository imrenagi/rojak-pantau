# rojak-pantau

We are using [Scrapy](https://doc.scrapy.org) as the base for `rojak-pantau`.
The reason of using this crawling framework are discussed below:

1. Fit the team needs. Any person who would like to add a new crawler for a media only need to add small changes to the source code.
2. Easy to deploy
3. Good at documentation

## Setup

* Install [docker](https://docs.docker.com/engine/installation/) and [docker-compose](https://docs.docker.com/compose/install/).
* Run the application by running `docker-compose up`

Notes: The crawler will not automatically run when the container has been created. To run the crawler, you need to go container console by doing this following steps:

* Run `docker ps` to see the list of running containers
* Note the `CONTAINER ID` of `rojak-spider`.
* Use `docker exec -it <CONTAINER ID> bash` to open the crawler console
* To run the crawler use this following command:
```
scrapy crawl pilkada_jabar_2018_merdekacom
```

Notes: Since the source code in the crawler container has been mounted to the source code in your host, you don't really have to copy paste the code to the container every time you make any changes on it because the changes you made in your editor will be automatically reflected in the container. So you can change the code from any text editor you want, and simply run the crawler within the container.

* The mysql database will be accessible in `localhost` from port `3307` instead of `3306`. so, if you already have mysql client in your machine, simply run
```
mysql --port=3307 --host=localhost --protocol=TCP --user=rojak --password=rojak
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
