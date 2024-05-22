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

def get_hash(data):
    """Calculate the hash of the given data."""
    data_string = ''.join(str(item) for item in data)
    return hashlib.sha256(data_string.encode()).hexdigest()

def load_previous_hash(file_path):
    """Load the previous hash from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()
    return None

def save_current_hash(file_path, current_hash):
    """Save the current hash to a file."""
    with open(file_path, 'w') as file:
        file.write(current_hash)

def save_to_csv(data, file_path):
    df = pd.DataFrame(data)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            existing_df = pd.read_csv(file_path)
            df = pd.concat([existing_df, df]).drop_duplicates().reset_index(drop=True)
        except pd.errors.EmptyDataError:
            pass  # The file is empty, so we'll just save the new data
    df.to_csv(file_path, index=False)


def max_ads(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all 'a' tags with the class 'dropdown-item'
    dropdown_items = soup.find_all('a', class_='dropdown-item')

    # Extract numbers from the text within these tags
    numbers = []
    for item in dropdown_items:
        text = item.get_text()
        found_numbers = re.findall(r'\d+', text)
        numbers.extend(found_numbers)

    # Convert found numbers to integers
    int_numbers = list(map(int, numbers))

    # Find the maximum number
    max_number = max(int_numbers)

    return max_number

def main(offset):
    base_url = 'https://hardverapro.hu/aprok/notebook/pc/index.html?offset='
    min_price = 0
    max_price = 9999
    all_ads = []

    max_num = max_ads(base_url)
    offset = int(offset)
    while offset <= max_num:
    url = f"{base_url}{offset}"
    ads = scrapeAds(url, min_price, max_price)
    if not ads:  # Stop if no more ads are found
        print(f"No ads found at offset {offset}. Stopping.")
        break
    all_ads.extend(ads)
    print(f"Scraped {len(ads)} ads from {url}")
    offset += 50
    # Calculate current hash of the scraped data
    current_hash = get_hash(all_ads)
    hash_file_path = 'data_hash.txt'

    # Load previous hash
    previous_hash = load_previous_hash(hash_file_path)

    if current_hash != previous_hash:
        print("New data found, updating CSV.")
        csv_file_path = 'data.csv'
        save_to_csv(all_ads, csv_file_path)
        save_current_hash(hash_file_path, current_hash)
    else:
        print("No new data found.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide an offset as a command-line argument")