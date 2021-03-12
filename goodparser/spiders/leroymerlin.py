import scrapy
from scrapy.http import HtmlResponse

from goodparser.items import GoodparserItem


class leroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru']

    def __init__(self, search):
        super(leroymerlinSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        goods_links = response.xpath("//a[@slot='name']/@href").extract()
        for link in goods_links:
            yield response.follow(link, callback=self.good_parse)

        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            return

    def good_parse(self, response: HtmlResponse):

        item_id = response.xpath("//uc-pdp-card-ga-enriched/@data-product-id").extract_first()
        item_name = response.xpath("//h1[@slot='title']/text()").extract_first()
        item_price = response.xpath("//uc-pdp-price-view[@slot='primary-price']//span[@slot='price']/text()").extract_first()
        item_price_currency = response.xpath(
            "//uc-pdp-price-view[@slot='primary-price']//span[@slot='currency']/text()").extract_first()
        item_price_unit = response.xpath(
            "//uc-pdp-price-view[@slot='primary-price']//span[@slot='unit']/text()").extract_first()
        item_price_second = response.xpath(
            "//uc-pdp-price-view[@slot='second-price']//span[@slot='price']/text()").extract_first()
        item_price_second_fract = response.xpath(
            "//uc-pdp-price-view[@slot='second-price']//span[@slot='fract']/text()").extract_first()
        item_price_second_currency = response.xpath(
            "//uc-pdp-price-view[@slot='second-price']//span[@slot='currency']/text()").extract_first()
        item_price_second_unit = response.xpath(
            "//uc-pdp-price-view[@slot='second-price']//span[@slot='unit']/text()").extract_first()
        item_pictures = response.xpath("//picture[@slot='pictures']/img/@src").extract()

        item_description = response.xpath(
            "//section[contains(@class,'pdp-section--product-description')]//text()").extract()
        item_properties = response.xpath(
            "//div[@class='def-list__group']//dt[@class='def-list__term']/text()").extract()
        item_properties_value = response.xpath(
            "//div[@class='def-list__group']//dd[@class='def-list__definition']/text()").extract()

        yield GoodparserItem(_id=item_id, name=item_name, href=response.url, pictures=item_pictures,
                             description=item_description,
                             properties=item_properties, properties_value=item_properties_value,
                             price=item_price, price_currency=item_price_currency, price_unit=item_price_unit,
                             price_second=item_price_second, price_second_fract=item_price_second_fract,
                             price_second_currency=item_price_second_currency, price_second_unit=item_price_second_unit)
