#code by funchooooza-ossh Good luck ;)
import requests
import fake_useragent
import random
import os
import json
import codecs
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from pathlib import Path
from lxml import etree
from database import db


class Scrapper:
    def url_list(baseurl, page_count):
        if baseurl.endswith('&page='):
            pass

        elif '&page=' in baseurl:
            parts=baseurl.split('&page=')
            if parts[-1].isdigit():
                baseurl=baseurl[:-1]
                    
        else:
             baseurl=baseurl+'&page='

        url_list = []
        for page in range(0,page_count):
            url = baseurl
            try:
                url_list.append(f'{url}{page}')
            except: break

        return(url_list)


    def page_count(soup):
        block = soup.find('main')
    
        if block:
            pager = block.find('div', class_='pager')
        
        if pager:
            pages_text = pager.get_text(strip=True)
            
            if 'дальше' in pages_text:
                pages_text = pages_text.split('дальше')[0]
                
            if '...' in pages_text:
                pages_text = pages_text.split('...')[-1]
            else:
                pages_text = pages_text[-1]
            
            try:
                pages = int(pages_text)
                return pages
            except ValueError:
                pass

        return 1
    
    
    def hrefs(url,session,headers):
        rs  = session.get(url,headers=headers).text
        soup = bs(rs,'html.parser')
        block = soup.find('main')
        cards = block.find_all('h2')

        href_list = []
        for card in cards:
            href=card.find('span')
            href = href.find('a')
            href_list.append(href['href'])
        return href_list


    def scrap(url):
        session = requests.Session()
        user=fake_useragent.FakeUserAgent().random
        headers = {

        'User-Agent':user

        }
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
        rs = session.get(url,headers=headers,proxies=proxies).text
        soup = bs(rs,'html.parser')
        try:
            vacancy = soup.find(attrs={'data-qa': 'vacancy-title'}).get_text() 
            vacancy = Scrapper.prettify(vacancy)

            try:
                salary = soup.find(attrs={'data-qa': 'vacancy-salary'}).get_text()
                salary = Scrapper.prettify(salary)
                
            except: salary = "Salary not presented"

            company =  soup.find(attrs={'data-qa': 'vacancy-company-name'}).get_text()
            company = Scrapper.prettify(company)
            
    

            location_dict = {
                'data-qa': ["vacancy-view-location","vacancy-view-raw-address"]
            }

            for value in location_dict['data-qa']:
                location = soup.find(attrs={'data-qa': value})
    
                if location:
                    location = location.text
                    location = Scrapper.prettify(location)
                    break
                else: continue
       
            print(url)

            description = soup.find(attrs={'data-qa': 'vacancy-description'}).get_text(strip=True)
            description = Scrapper.prettify(description)
            
            db.inputdata(vacancy, salary, company, location, description, url)
            
        except: pass
               
                    
    def prettify(smth):
        smth=smth.replace("'","")
        return smth
