import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    # start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords = sql']
    start_urls = ['https://russia.superjob.ru/vakansii/data-engineer.html']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        vacancies_links = response.xpath("//div[@class='_3mfro PlM3e _2JVkc _3LJqf']//a/@href").extract()
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacansy_parse)

        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            return

    def vacansy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1[@class='_3mfro rFbjy s1nFK _2JVkc']/text()").extract_first()
        item_salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        yield JobparserItem(name=item_name, salary=item_salary, href=response.request.url, site=self.name)
