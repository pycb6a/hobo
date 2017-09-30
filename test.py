import argparse
import contextlib
import json
import logging
import os
import unittest

import yaml
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from xmlrunner.runner import XMLTestRunner

from hobo.spiders.hobo import Hobo

logger = logging.getLogger()


class ItemTest(unittest.TestCase):
    assertions = {}
    items = []

    @classmethod
    def setUpClass(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', default='config.yml')

        with open(parser.parse_args().config, 'r') as f:
            config = yaml.load(f)

        settings = config.get('settings')
        with contextlib.suppress(FileNotFoundError):
            os.remove(settings.get('feed_uri'))

        custom_settings = {}
        if settings:
            custom_settings = {k.upper(): v for k, v in settings.items()}

        cls.assertions = config.get('assertions')

        project_settings = get_project_settings()
        project_settings.update(custom_settings)
        process = CrawlerProcess(project_settings)
        process.crawl(Hobo, config=config)
        process.start()

        with open(settings.get('feed_uri'), 'r') as f:
            cls.items = json.load(f)

    def test_count(self):
        self.assertGreater(len(ItemTest.items), 0, 'There are collected items')

    def test_item(self):
        for item in ItemTest.items:
            with self.subTest(item=item):
                for assertion in ItemTest.assertions:
                    matcher = assertion.get('matcher')
                    if matcher:
                        method = ''
                        args = []

                        def assert_(text):
                            return 'assert' + ''.join(x for x in text.title() if not x.isspace())

                        if None not in matcher:
                            method = assert_(matcher[0])
                            args = matcher[1:]
                            args.insert(0, item[assertion['key']])
                        elif matcher[0] is None:
                            method = assert_(matcher[1])
                            args = matcher[2:]
                            args.insert(0, item[assertion['key']])
                        elif None in matcher[1:]:
                            method = assert_(matcher[1])
                            args = [matcher[0], item[assertion['key']]]
                            args.extend([m for m in matcher[2:] if m is not None])
                        getattr(self, method)(*args, assertion.get('description'))


if __name__ == '__main__':
    unittest.main(
        testRunner=XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False)
