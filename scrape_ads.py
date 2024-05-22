import traceback
import re
import requests
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import os

def getURLParams(url):
    parsed_url = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(parsed_url.query)

def fetch_content(url):
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")
    price_html = html.find("h2", class_="text-center text-md-left")
    price = price_html.get_text()
    uad_content = html.find("div", class_="uad-content")

    rtif_content = uad_content.find("div", class_="mb-3 rtif-content")
    if rtif_content:
        text_content = rtif_content.get_text(separator=" ", strip=True)
        return text_content
    else:
        return ""

def scrapeCategoryName(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        html = BeautifulSoup(response.text, "html.parser")
        category_name = html.find("div", id="top").find("ol", class_="breadcrumb").find_all("li", class_="breadcrumb-item")[-1].text

        return category_name or "n/a"

    except Exception as err:
        traceback.print_exc()

    return "n/a"

def find_date(url):
    response = requests.get(url)
    response.raise_for_status()
    html = BeautifulSoup(response.text, "html.parser")
    date_span = html.find('span', {'data-toggle': 'tooltip', 'title': 'Feladás időpontja'})
    if not date_span:
        print(f"html: {html}, link : {url}")
    return date_span.get_text()

def scrapeAds(url, min_price, max_price):
    try:
        response = requests.get(url)
        response.raise_for_status()

        parsed_url = urllib.parse.urlparse(url)
        base_url = parsed_url.scheme + '://' + parsed_url.netloc

        html = BeautifulSoup(response.text, "html.parser")
        uad_list = html.find("div", class_="uad-list")

        ads = []
        if uad_list and uad_list.ul and uad_list.ul.li:
            medias = html.findAll(class_="media")
            
            for ad in medias:
                title = ad.find("div", class_="uad-title")
                info = ad.find("div", class_="uad-info")
                misc = ad.find("div", class_="uad-misc")

                if title and info:
                    info_divs = info.findAll("div")
                    misc_divs = misc.findAll("div")
                    price_text = info_divs[0].text.strip().replace(',', '').replace(' ', '')
                    price_value = ''.join(filter(str.isdigit, price_text))
                    if price_value.isdigit():
                        price = int(price_value)
                        if len(info_divs) >= 3 and len(misc_divs) >= 2 and min_price*1000 <= price <= max_price*1000:
                            link = title.h1.a["href"]
                            if link:
                                date = find_date(title.h1.a["href"])
                            else:
                                date = info_divs[2].text.strip()
                            ads.append({
                                "id": ad["data-uadid"],
                                "name": title.h1.a.text.strip(),
                                "link": link,
                                "price": info_divs[0].text.strip(),
                                "city": info_divs[1].text.strip(),
                                "date": date,
                                "seller_name": misc_divs[0].a.text.strip(),
                            })
        return ads

    except Exception as err:
        traceback.print_exc()

    return []

def save_to_csv(data, file_path):
    df = pd.DataFrame(data)
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        df = pd.concat([existing_df, df]).drop_duplicates().reset_index(drop=True)
    df.to_csv(file_path, index=False)

url = 'https://hardverapro.hu/aprok/notebook/pc/index.html?offset='
ads = scrapeAds(url, 0, 9999)
csv_file_path = 'data.csv'
save_to_csv(ads, csv_file_path)
