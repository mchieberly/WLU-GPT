import requests 
from bs4 import BeautifulSoup
import json
from tqdm import tqdm 
import re  

# URL handling and setup
sitemap_url = 'https://my.wlu.edu/google-site-map.xml'  # Sitemap URL

# Session for efficient network requests
session = requests.Session()

# Fetch the sitemap
response = session.get(sitemap_url)
response.raise_for_status()  # Will raise an error for bad responses

# Parse the XML content of the sitemap using BeautifulSoup for simplicity
sitemap_soup = BeautifulSoup(response.content, 'xml')
urls = ["https://my.wlu.edu/" + loc.text for loc in sitemap_soup.find_all('loc')]


# List of URLs to exclude or block
block_list = ["https://my.wlu.edu/financial-aid/types-of-aid/loans/doe-exit-counseling"]

# Data list for storing scraped content
data = []

min_length = 50  # Minimum text length to consider

# Progress bar with tqdm
for url in tqdm(urls):
    # Skip irrelevant URLs 
    if url.endswith('.xml') or url in block_list:
        continue
    
    try:
        response = session.get(url)
        response.raise_for_status()  # Check for request success
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Enhanced text extraction with more tags and content filtering
        tags = ['p', 'h1', 'h2', 'h3', 'li', 'article', 'section']  # Extended list of tags
        texts = [element.text.strip() for element in soup.find_all(tags)]
        full_text = ' '.join(texts)
        
        # Basic text cleaning and normalization
        full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
        full_text = full_text.lower()  # Standardize case
        
        # Filter out empty or very short texts
        if len(full_text) > min_length:  # Minimum length
            data.append({
                "url": url,  # Include URL for context
                "note": full_text
            })

    except Exception as e:
        # Log errors to a file instead of printing
        with open('raw/error_log.txt', 'a') as log_file:
            log_file.write(f'Failed to process {url}: {e}\n')

# Saving cleaned and structured data to a `.jsonl` file
with open('raw/notes.jsonl', 'w') as f:
    for entry in data:
        json.dump(entry, f)
        f.write('\n')