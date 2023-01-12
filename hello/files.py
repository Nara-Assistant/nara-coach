import requests

def download_file(url, name):
    r = requests.get(url, stream=True)
    print(r.content)
    with open(f"{name}", 'wb') as fd:
        for chunk in r.iter_content(2000):
            fd.write(chunk)

# download_pdf("https://www.irs.gov/pub/irs-pdf/f1040.pdf")
