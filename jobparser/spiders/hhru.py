import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://rostov.hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=data+engineer']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").extract_first()
        vacancies_links = response.css("a.bloko-link.HH-LinkModifier::attr(href)").extract()
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacansy_parse)

        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            return

    def vacansy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1/text()").extract_first()
        item_salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        yield JobparserItem(name=item_name, salary=item_salary)



