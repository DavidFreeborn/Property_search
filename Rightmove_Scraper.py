import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urlencode, urlparse, parse_qs
import re

def scrape_rightmove(url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    properties = []
    page = 0

    while True:
        print(f"Scraping page {page + 1}...")
        current_url = update_url(url, page)
        response = requests.get(current_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        scripts = soup.find_all('script')
        json_data = None

        for script in scripts:
            if script.string and 'window.jsonModel = ' in script.string:
                print("Found script with window.jsonModel")
                json_text = script.string.split('window.jsonModel = ', 1)[-1].strip()
                json_text = re.sub(r';?\s*$', '', json_text)
                
                try:
                    json_data = json.loads(json_text)
                    print("Successfully parsed JSON data")
                    break
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print("Extracted JSON string (first 200 characters):")
                    print(json_text[:200])

        if not json_data:
            print("Couldn't find any JSON data with property information")
            break

        properties_data = json_data.get('properties', [])

        if not properties_data:
            print("No properties found on this page.")
            break

        for prop in properties_data:
            location = prop.get('location', {})
            latitude = location.get('latitude')
            longitude = location.get('longitude')
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}" if latitude and longitude else ""

            property_info = {
                'price': prop.get('price', {}).get('amount'),
                'bedrooms': prop.get('bedrooms'),
                'propertySubType': prop.get('propertySubType'),
                'address': prop.get('displayAddress'),
                'location': google_maps_url,
                'url': f"https://www.rightmove.co.uk/properties/{prop.get('id')}",
                'formattedBranchName': prop.get('customer', {}).get('branchDisplayName'),
                'addedOrReduced': prop.get('addedOrReduced'),
                'firstVisibleDate': prop.get('firstVisibleDate'),
                'displaySize': prop.get('displaySize'),
                'productLabel': prop.get('productLabel', {}).get('productLabelText')
            }
            properties.append(property_info)

        print(f"Found {len(properties_data)} properties on this page")
        page += 1
        
        total_results = json_data.get('resultCount')
        if total_results is not None:
            try:
                total_results = int(total_results)
                if len(properties) >= total_results:
                    print(f"Reached the end of results. Total properties: {total_results}")
                    break
            except ValueError:
                print(f"Warning: Couldn't convert resultCount to integer: {total_results}")
        else:
            print("Warning: Couldn't find resultCount in JSON data")

    unique_properties = list({prop['url']: prop for prop in properties}.values())
    print(f"Removed {len(properties) - len(unique_properties)} duplicate properties")

    # Write to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(unique_properties[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for prop in unique_properties:
            writer.writerow(prop)

    print(f"Scraping complete. {len(unique_properties)} unique properties saved to {output_file}")

def update_url(url, page):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['index'] = [str(page * 24)]
    query_params['numberOfPropertiesPerPage'] = ['499']
    new_query = urlencode(query_params, doseq=True)
    return parsed_url._replace(query=new_query).geturl()

# Construct the URL with the given parameters
base_url = "https://www.rightmove.co.uk/property-for-sale/find.html"
params = {
    'locationIdentifier': 'USERDEFINEDAREA^{"id":8791529}',
    'minBedrooms': 1,
    'maxPrice': 300000,
    'minPrice': 240000,
    'propertyTypes': 'flat',
    'includeSSTC': 'false',
    'mustHave': '',
    'dontShow': '',
    'furnishTypes': '',
    'keywords': '',
    'sortType': 6,
    'numberOfPropertiesPerPage': 499,
    'viewType': 'LIST'
}

url = base_url + '?' + urlencode(params)

# Run the scraper
scrape_rightmove(url, 'rightmove_properties_streamlined.csv')

