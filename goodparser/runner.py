from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from goodparser import settings
from goodparser.spiders.leroymerlin import leroymerlinSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(leroymerlinSpider, 'обои')
    process.start()
