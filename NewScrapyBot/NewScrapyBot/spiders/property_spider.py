import scrapy
from ..items import NewscrapybotItem
import time
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class PropertySpider(scrapy.Spider):
    name = "propertySpider"
    start_urls = ["https://www.justdial.com/Delhi/House-On-Rent/nct-10192844/page-1"]
    page_no = 2
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument(" --disable-gpu")
    options.add_argument(" --disable-infobars")
    caps = options.to_capabilities()
    handle_httpstatus_list = [403, 504]

    def parse(self, response):
        driver = webdriver.Chrome('/Users/INDRA/Desktop/Scrapybot/NewScrapyBot/chromedriver',
                                  desired_capabilities=self.caps)
        driver.get("https://www.justdial.com/Delhi/House-On-Rent/nct-10192844/page-{}".format(self.page_no-1))
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(8)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            time.sleep(7)

        items = NewscrapybotItem()
        scrapy_selector = Selector(text=driver.page_source)
        all_div_properties = scrapy_selector.css("li.cntanr")

        switcher = {
            'acb': '0',
            'yz"': '1',
            'wx"': '2',
            'vu"': '3',
            'ts"': '4',
            'rq"': '5',
            'po"': '6',
            'nm"': '7',
            'lk"': '8',
            'ji"': '9',
            'dc"': '+',
            'ba"': '-',
            'fe"': '(',
            'hg"': ')'
        }

        for property in all_div_properties:
            name = property.css("span.lng_cont_name::text").extract_first()
            rating = float(property.css("span.green-box::text").extract_first())
            address = property.css("span.cont_sw_addr::text").extract_first()[13:-9]

            contact_info = property.css("p.contact-info").css("span")
            phone_no = ''
            for number in contact_info:
                str_n = number.css("span.mobilesv").extract_first()[27:30]
                phone_no += switcher[str_n]

            items['name'] = name
            items['rating'] = rating
            items['phone'] = phone_no[-10:]
            items['address'] = address

            yield items

        driver.close()

        next_page = "https://www.justdial.com/Delhi/House-On-Rent/nct-10192844/page-{}".format(self.page_no)
        print(next_page)
        if self.page_no<=50:
            self.page_no += 1
            yield response.follow(next_page, callback=self.parse)
