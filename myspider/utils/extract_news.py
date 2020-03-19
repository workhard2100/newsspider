# -*- coding: utf-8 -*-

from gne import GeneralNewsExtractor


class NewsParser:
    
    def extract_news(self, html):
        extractor = GeneralNewsExtractor()
        result = extractor.extract(html, noise_node_list=['//div[@class="comment-list"]'])
        return result