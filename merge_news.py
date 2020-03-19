# -*- conding:utf8 -*-
import os
import datetime
import pandas


def merge(publish_time='20200319104500', lange='zh'):
    fp = os.path.dirname( os.path.abspath(__file__)) + '\\'
    news_path = fp + '\\myspider\\data\\news\\'
    data = []
    for f in os.listdir(news_path):
        if '%s_%s'%(lange, publish_time[:8]) in f:
            content = eval(open(news_path+f,'r',encoding='utf-8').read())
            time_str = datetime.datetime.strptime(publish_time,'%Y%m%d%H%M%S')
            time_str = datetime.datetime.strftime(time_str, '%Y-%m-%d %H:%M')
            row = [content['title'],time_str,content['url'],content['content']]
            data.append(row)
    df = pandas.DataFrame(data,columns=['title','time','url','content'])
    save_path = news_path + publish_time[:8] + '.csv'
    df.to_csv(save_path,index=False, encoding='utf-8')
            
    

def run():
    date = datetime.datetime.strftime(datetime.datetime.now()+datetime.timedelta(hours=-8),"%Y%m%d%H%M%S")
    merge(date)


if __name__ == "__main__":

    run()
