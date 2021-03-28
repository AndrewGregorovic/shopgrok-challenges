import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"

    def start_requests(self):
        urls = [
            "https://www.aldi.com.au/",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    def parse_categories(self, response):
        # Get the category list from the home page and iterate over it
        # to get product information from each category
        for category in response.xpath("//nav[@id='main-nav']/ul/li[2]/div[2]/ul/li"):
            yield scrapy.Request(url=category.xpath("./div/a/@href").extract_first(), callback=self.parse_products)

    def parse_products(self, response):
        # Iterate over products listed on the page
        for product in response.xpath("//div[@class='tx-aldi-products']/div/a"):

            # Get packsize data
            packsize = product.xpath(".//span[@class='box--amount']/text()").extract()
            packsize = self.return_element_if_list_not_empty(packsize)

            # Get price data, idk why they have to separate it into 2 fields
            price = product.xpath(".//span[@class='box--value']/text()").extract()
            price_decimal = product.xpath(".//span[@class='box--decimal']/text()").extract()
            price = self.return_element_if_list_not_empty(price)

            # Concatenate the value and decimal fields if necessary or append c for prices under a dollar
            if price and price[0] == "$":
                price += self.return_element_if_list_not_empty(price_decimal)
            elif price and price[0] != "$":
                price += "c"

            # Get price per unit data
            price_per_unit = product.xpath(".//span[@class='box--baseprice']/text()").extract()
            price_per_unit = self.return_element_if_list_not_empty(price_per_unit)

            yield {
                "product_title": product.xpath("normalize-space(.//div[@class='box--description--header'])").extract()[0].replace("\xa0", " ").strip(),
                "product_image": product.xpath(".//div/div/div/img/@src").extract()[0],
                "packsize": packsize,
                "price": price,
                "price per unit": price_per_unit
            }

        # If page contains subcategories and no products, scrape each subcategory page
        for subcategory in response.xpath("//div[@class='csc-textpic-imagewrap']/div/div/a"):
            yield scrapy.Request(url=subcategory.xpath("./@href").extract_first(), callback=self.parse_products)

    def return_element_if_list_not_empty(self, list):
        # Little function to make the code a bit DRY-er and avoid errors with empty lists
        return list[0] if list != [] else ""
