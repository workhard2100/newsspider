# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os, re
import json

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

class MyspiderPipeline(object):
    data_path = os.path.dirname(os.path.abspath(__file__)) + '\\data\\'
    
    def process_item(self, item, spider):
        news_path = self.data_path +'news' + '\\'
        if not os.path.exists(news_path):
            os.makedirs(news_path)
        filename = news_path + item['langid'] + '_' + item['id'] + '.json'
        with open(filename,'w+', encoding='utf-8') as file_obj:
            file_obj.write(str(item))
        #print('title:',item['url'])
        return item
