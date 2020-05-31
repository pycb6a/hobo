from urllib.parse import urlparse

from loginform import fill_login_form
from scrapy import Request, FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class Hobo(CrawlSpider):
    name = 'hobo'

    def __init__(self, config, *a, **kw):
        site = config.get('site')
        if site:
            self.url = site.get('url')
            self.auth_path = site.get('auth_path')
            self.login = site.get('login')
            self.password = site.get('password')

        rule = config.get('rule')
        parsed_url = urlparse(self.url)
        self.allowed_domains = (parsed_url.netloc, parsed_url.hostname)

        self.rules = (
            Rule(LinkExtractor(allow_domains=(parsed_url.netloc,), **rule),
                 callback='parse_start_url', follow=True),
        )

        self.assertions = config.get('assertions')
        super().__init__(*a, **kw)

    def start_requests(self):
        if self.auth_path and self.login and self.password:
            request = Request(url=self.url + self.auth_path, callback=self.logged_in)
        else:
            request = Request(url=self.url)
        yield request

    def logged_in(self, response):
        args, url, method = fill_login_form(response.url, response.body, self.login, self.password)
        return FormRequest(response.url, method=method, formdata=args)

    def parse_start_url(self, response):
        item = {'url': response.url, }
        for assertion in self.assertions:
            if assertion.get('attribute') == 'status':
                item[assertion['key']] = getattr(response, 'status')
            elif assertion.get('attribute') == 'headers':
                header = response.headers.get(assertion.get('field'))
                item[assertion['key']] = header.decode() if header else None
            elif assertion.get('attribute') == 'text':
                selector = assertion.get('selector')
                if selector:
                    nodes = getattr(response, selector['by'])(selector['path'])
                    first = '_first' if selector['extract'] == 'first' else ''
                    text = getattr(nodes, 'extract' + first)()
                    item[assertion['key']] = text
        return item
