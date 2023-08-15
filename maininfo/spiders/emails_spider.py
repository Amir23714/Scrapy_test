import asyncio
import re
import time
from maininfo.settings import logging
import scrapy

from TXT_parsing.txt_to_list import parse_txt
from TXT_parsing.validate_url import validate_url

from CSVwriter import CSVwriter

# Patterns that are used to validate founded information from the sites
patterns = {
    "phone": r'\+7\d{10}|8\d{10}',
    "strange_phone": r'\+7\(\d{3}\)\d{3}-\d{2}-\d{2}|8\(\d{3}\)\d{3}-\d{2}-\d{2}',
    "email": r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    "inn": r'\b\d{10}\b',
    "ogrn": r'\b\d{13}\b',
    "postal_code": r'\b\d{6}\b',
}

# Initializing CSVwriter class
csvwriter = CSVwriter()
asyncio.run(csvwriter.init_csv())


class QuotesSpider(scrapy.Spider):
    name = 'emails'

    def start_requests(self):
        # Parse domain URLs and block URLs from files
        urls = parse_txt("Static_files\\domains.txt")
        blocked = parse_txt("Static_files\\block_domains.txt")
        urls = validate_url(urls, blocked)

        start = time.time()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.handle_error)

        print("Time took ", time.time() - start)

    async def parse(self, response, depth=0):
        # Extract title and description
        title = response.css("title::text").get() or "н/д"
        description = response.css('meta[name="description"]::attr(content)').get() or "н/д"

        # Variables for storing important data to be written to .csv
        emails = []
        phones = []
        postal_codes = []
        inns = []
        ogrns = []

        decoded_body = response.body.decode('utf-8')

        # Find and process phone numbers
        phones_temp = re.findall(patterns["phone"], decoded_body)
        for phone in phones_temp:
            if phone not in phones:
                phones.append(phone)

        phones_temp = re.findall(patterns["strange_phone"], decoded_body)
        for phone in phones_temp:
            if phone not in phones:
                phones.append(phone)

        # Find and process email addresses
        emails_temp = re.findall(patterns["email"], decoded_body)
        for email in emails_temp:
            if email not in emails:
                emails.append(email)

        # Find and process INN numbers
        inns_temp = re.findall(patterns["inn"], decoded_body)
        for inn in inns_temp:
            if inn not in inns:
                inns.append(inn)

        # Find and process OGRN numbers
        ogrns_temp = re.findall(patterns["ogrn"], decoded_body)
        for ogrn in ogrns_temp:
            if ogrn not in ogrns:
                ogrns.append(ogrn)

        # Find and process postal codes
        postal_codes_temp = re.findall(patterns["postal_code"], decoded_body)
        for code in postal_codes_temp:
            if code not in postal_codes:
                postal_codes.append(code)

        # Join lists into strings, or default to "н/д"
        emails = "\n".join(emails) or "н/д"
        phones = "\n".join(phones) or "н/д"
        postal_codes = "\n".join(postal_codes) or "н/д"
        inns = "\n".join(inns) or "н/д"
        ogrns = "\n".join(ogrns) or "н/д"

        # Write data to CSV
        await csvwriter.fill_csv(response.url, title, description, emails, phones, postal_codes, inns, ogrns)

        # Extract contact links and follow them recursively
        contacts_links = response.xpath(
            '//a[contains(text(), "Контакты") or contains(text(), "Contacts")]/@href').extract()

        used_links = []

        if depth < 1:
            for link in contacts_links:
                if link not in used_links:
                    used_links.append(link)
                    link = response.urljoin(link)
                    yield scrapy.Request(url=link, callback=self.parse, meta={'depth': 1}, errback=self.handle_error)

    async def handle_error(self, failure):
        logging.error(f"Parsing error\n url : {failure.request.url}\ndetails : {failure.getErrorMessage()}")
