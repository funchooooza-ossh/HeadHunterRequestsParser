# code by funchooooza-ossh Good luck ;)
import time
import requests
import fake_useragent
import random
import os
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from pathlib import Path
from database import db


class Scrapper:
    def url_list(baseurl, page_count):
        if baseurl.endswith("&page="):
            pass

        elif "&page=" in baseurl:
            parts = baseurl.split("&page=")
            if parts[-1].isdigit():
                baseurl = baseurl[:-1]

        else:
            baseurl = baseurl + "&page="

        url_list = []
        for page in range(0, page_count):
            url = baseurl
            url_list.append(f"{url}{page}")

        return url_list

    def page_count(soup):
        block = soup.find("main")

        if block:
            pager = block.find("div", class_="pager")

        if pager:
            pages_text = pager.get_text(strip=True)
            if "дальше" in pages_text:
                pages_text = pages_text.split("дальше")[0]
            if "..." in pages_text:
                pages_text = pages_text.split("...")[-1]
            else:
                pages_text = pages_text[-1]
            try:
                pages = int(pages_text)
                return pages
            except ValueError:
                pass
        return 1

    def hrefs(url, session, headers, max_retries, retry_delay):
        attempts = 0
        while attempts < max_retries:
            try:
                rs = session.get(url, headers=headers)
                rs.raise_for_status()  # проверка статуса ответа
                soup = bs(rs.text, "lxml")

                block = soup.find("main")
                if not block:
                    raise ValueError("Не удалось найти блок c вакансиями на странице")

                cards = block.find_all("h2")
                href_list = []
                for card in cards:
                    href = card.find("span")
                    if href:
                        href = href.find("a")
                        if href and "href" in href.attrs:
                            href_list.append(href["href"])
                        else:
                            raise ValueError("Не удалось найти ссылку в элементе")
                    else:
                        raise ValueError("Не удалось найти элемент 'span'")

                return href_list
            except Exception as e:
                print(f"Попытка {attempts + 1} из {max_retries} не удалась: {e}")
                attempts += 1
                if attempts < max_retries:
                    time.sleep(retry_delay)

        raise Exception(f"Не удалось получить ссылки после {max_retries} попыток")

    def scrap(url, max_retries=3, retry_delay=1):
        session = requests.Session()
        user = fake_useragent.FakeUserAgent().random
        headers = {"User-Agent": user}
        dotenv_path = Path(".", ".env")
        load_dotenv(dotenv_path)
        proxylist = [os.getenv("PROXY1"), os.getenv("PROXY2"), os.getenv("PROXY3")]
        proxy = random.choice(proxylist)

        proxies = {"http": proxy, "https": proxy}
        for attempt in range(max_retries):
            try:
                rs = session.get(url, headers=headers, proxies=proxies)
                rs.raise_for_status()
                soup = bs(rs.text, "lxml")

                vacancy = soup.find(attrs={"data-qa": "vacancy-title"}).get_text()
                vacancy = Scrapper.prettify(vacancy)

                try:
                    salary = soup.find(attrs={"data-qa": "vacancy-salary"}).get_text()
                    salary = Scrapper.prettify(salary)
                except:
                    salary = "Salary not presented"

                company = soup.find(
                    attrs={"data-qa": "vacancy-company-name"}
                ).get_text()
                company = Scrapper.prettify(company)

                location = None
                location_qa_list = ["vacancy-view-location", "vacancy-view-raw-address"]
                for qa in location_qa_list:
                    location_elem = soup.find(attrs={"data-qa": qa})
                    if location_elem:
                        location = Scrapper.prettify(location_elem.text)
                        break
                if not location:
                    location = "Location not specified"

                description = soup.find(
                    attrs={"data-qa": "vacancy-description"}
                ).get_text(strip=True)
                description = Scrapper.prettify(description)

                db.inputdata(vacancy, salary, company, location, description, url)

                print(f"Data fetched successfully from {url}")
                break
            except Exception as e:
                print(f"Error fetching data from {url}: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying... ({attempt+2}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Moving to the next URL")

    def prettify(smth):
        smth = smth.replace("'", "")
        return smth
