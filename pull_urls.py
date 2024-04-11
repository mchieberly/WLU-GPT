import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

# URL of the sitemap
sitemap_url = 'https://my.wlu.edu/google-site-map.xml'  # Replace with the actual sitemap URL

# Fetch the sitemap
response = requests.get(sitemap_url)
print(response)

# Parse the XML content of the sitemap
sitemap_xml = ET.fromstring(response.content)

# Namespace to use for finding elements, based on your sitemap's structure
namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

# Extract URLs
urls = [url.text for url in sitemap_xml.findall('.//ns:url/ns:loc', namespaces)]
for i in range(len(urls)):
    urls[i] = "https://my.wlu.edu/" + urls[i]

# Print the URLs to verify
#for url in urls:
    #print(url)


# Replace this with the actual list of pages you want to scrape

data = []

for i in tqdm(range(len(urls))):
    url = urls[i]
    # Skip URLs ending with '.xml'
    if not url.endswith('.xml'):
        try:
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract all text: combine the texts of certain elements, e.g., paragraphs
                texts = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])  # Adjust tags as needed
                full_text = ' '.join([element.text.strip() for element in texts])
                
                data.append({"note": full_text})
        except Exception as e:
            print(f'Failed to process {url}: {e}')

# Saving data to a `.jsonl` file
with open('data/notes.jsonl', 'w') as f:
    for entry in data:
        json.dump(entry, f)
        f.write('\n')