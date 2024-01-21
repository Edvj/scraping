import requests
from bs4 import BeautifulSoup
import json
import logging
import configparser
import time

# Load the configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Set up logging
log_file = config['logging']['log_file']
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get scraping configuration
base_url = config['scraping']['url']
product_item_selector = config['scraping']['product_item_selector']
title_selector = config['scraping']['title_selector']
price_selector = config['scraping']['price_selector']
wait_time = int(config['scraping']['wait_time'])
max_pages = int(config['scraping'].get('max_pages', 10))  # Default to 10 if not specified

# Get output configuration
log_to_console = config.getboolean('output', 'log_to_console')
output_file = config['output']['output_file']

scraped_data = []

# Loop through the specified number of pages
for page in range(1, max_pages + 1):
    # Construct the paginated URL
    url = f"{base_url}?page={page}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f'Successfully retrieved the webpage: {url}')
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            product_items = soup.select(product_item_selector)

            for item in product_items:
                title_tag = item.select_one(title_selector)
                product_title = title_tag.text.strip() if title_tag else 'No Title'

                price_tag = item.select_one(price_selector)
                product_price = price_tag.text.strip() if price_tag else 'No Price'

                scraped_data.append({'Product Title': product_title, 'Price': product_price})
                time.sleep(wait_time)  # Wait before processing the next item

        else:
            logging.error(f'Failed to retrieve the webpage: {url}. Status code: {response.status_code}')
            break  # Exit the loop if a page fails to load

    except Exception as e:
        logging.exception(f'An error occurred: {e}')
        break  # Exit the loop if an exception occurs

    if not product_items:
        logging.info('No more products found, assuming last page.')
        break  # Exit the loop if no products are found on the page

# Write the scraped data to a JSON file
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(scraped_data, file, ensure_ascii=False, indent=4)
logging.info('Data scraped and saved to ' + output_file)

if log_to_console:
    print(json.dumps(scraped_data, ensure_ascii=False, indent=4))

