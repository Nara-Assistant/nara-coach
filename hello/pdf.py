from dotenv import load_dotenv
import os

# Use load_env to trace the path of .env:
load_dotenv('.env')
import requests

def download_pdf(url):
    r = requests.get(url, stream=True)
    print(r.content)
    with open(f'metadata.pdf', 'wb') as fd:
        for chunk in r.iter_content(2000):
            fd.write(chunk)

# download_pdf("https://www.irs.gov/pub/irs-pdf/f1040.pdf")
