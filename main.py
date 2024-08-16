#code by funchooooza-ossh Good luck ;)
import requests
import fake_useragent
import random
import os
from dotenv import load_dotenv
from pathlib import Path
from lxml import etree
from bs4 import BeautifulSoup as bs
from scrap import Scrapper
from multiprocessing.pool import Pool

def main():
    print("#code by funchooooza-ossh Good luck ;)")
    dotenv_path = Path('.','.env')
    load_dotenv(dotenv_path)
    proxylist = [
        os.getenv('PROXY1'),
        os.getenv('PROXY2'),
        os.getenv('PROXY3')
    ]
    proxy=random.choice(proxylist)
    

    proxies = {
        'http':proxy,
        'https':proxy
    }

    user=fake_useragent.FakeUserAgent().random
    session=requests.Session()
    headers = {
        'User-Agent':user
    }
   
    url = input('Input your url:\n')

    if url.find('items_on_page=100')!= -1:
        url = url.replace('items_on_page=100','items_on_page=20')
    elif url.find('items_on_page=50')!= -1:
        url = url.replace('items_on_page=50','items_on_page=20')

    rs = session.get(url, headers=headers,proxies=proxies).text

    soup = bs(rs,'html.parser')
    dom = etree.HTML(str(soup))
    count_xpath = './/h1'
    count = dom.xpath(count_xpath)[0].text
    count = ''.join(count.split())
    count  = int(count)
    print (f'Vacancies catched:{count} vacancies')

    pages = Scrapper.page_count(soup)
    print(f'Total pages: {pages}')

    urls = Scrapper.url_list(url,pages)
    process_count = input('Input process count:')
    print(f'Starting with {process_count} processes')
    for ur in urls:
        hrefs = Scrapper.hrefs(ur,session,headers)
        
        try:
            p = Pool(processes=int(process_count))
            p.map(Scrapper.scrap,hrefs)
        except Exception as ex:
            print(ex)           



    



if __name__ == '__main__':
    main()
