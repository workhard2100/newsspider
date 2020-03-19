# -*- coding: utf-8 -*-
import scrapy
import os
import requests
import shutil
import zipfile
import pandas

import langid

from urllib.request import urlopen
from requests.adapters import HTTPAdapter


from myspider.utils.extract_news import *
from myspider.items import MyspiderItem

def un_zip(filename_full, savepath):
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    zip_file = zipfile.ZipFile(filename_full)
    for names in zip_file.namelist():
        zip_file.extract(names, savepath)
    zip_file.close()
    os.remove(filename_full)
    
def get_savepath(filename, savepath):
    month = filename.split('.')[0][0:6]
    if not os.path.isdir(savepath+month):
        os.mkdir(savepath+month)
    return savepath+month+'\\'

def download(filename, savepath):
    if os.path.exists(get_savepath(filename, savepath)+filename.strip('.zip')):
        print('%s exist!!!' % filename)
        return 0
    url = 'http://data.gdeltproject.org/gdeltv2/%s' % filename
    response = requests.get(url, stream=True)
    length = float(response.headers['content-length'])
    with open(savepath+filename, "wb") as code:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                code.write(chunk)
    if not os.path.isdir(get_savepath(filename, savepath)):
        os.mkdir(savepath+month)
    try:
        un_zip(savepath+filename, get_savepath(filename, savepath))
    except Exception as e:
        print('un_zip %s Error: %s' % (filename,str(e)))
        os.remove(savepath+filename)
    return 0
    
def download_lastupdate(savepath, filetype):
    url = 'http://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt'
    html = urlopen(url).read()
    filename = None
    for line in str(html.decode('utf-8')).split('\n'):
        if filetype.lower() not in line.lower():
            #print(line)
            continue
        filename = line.split(' ')[-1].split('/')[-1].strip()
    if not filename:
        print('get filename error!!')
        return 
    download(filename, savepath)
    return filename
    
class GdeltSpider(scrapy.Spider):
    name = 'gdelt'
    allowed_domains = ['data.gdeltproject.org']
    start_urls = ['http://data.gdeltproject.org/']
    filename = None #'20200319010000.translation.gkg.csv.zip'
    file_type = '.translation.gkg.CSV.zip'
    dataPath = os.path.dirname(os.path.abspath(__file__)) + '\\..\\data\\'

    def start_requests(self):
        self.filename = download_lastupdate(self.dataPath, self.file_type)
        urls = set()
        data = pandas.read_csv(get_savepath(self.filename, self.dataPath) + self.filename.strip('.zip'),sep='\t',usecols=[4])
        for i, u in data.iterrows():
            urls.add(str(u[0]).strip())
        print('url num:', len(urls))
        for index,url in enumerate(list(urls)):
            #if index > 10:
            #    return
            id = self.filename.split('.')[0] + '_' + str(index)
            param = {'id': id}
            yield scrapy.Request(url=url,encoding='utf-8',callback=self.parse, meta=param)

    def parse(self, response):
        print('*'*80)
        print(response.meta['id'])
        np = NewsParser()
        result = np.extract_news(response.text)
        if not result:
            return
        item = MyspiderItem()
        item['id'] = response.meta['id']
        item['url'] = response.url
        item['title'] = result['title']
        item['publish_time'] = result['publish_time']
        item['author'] = result['author']
        item['content'] = result['content']
        item['langid'] = langid.classify(item['title'])[0]
        print(item['langid'])
        if item['langid'] in ['zh', 'en']: #en
            yield item
