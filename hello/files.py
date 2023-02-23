import requests
import os.path

def download_file(url, name):

    if os.path.isfile(name) is False:
        r = requests.get(url, stream=True)
        print(r.content)
        with open(f"{name}", 'wb') as fd:
            for chunk in r.iter_content(2000):
                fd.write(chunk)



# download_pdf("https://www.irs.gov/pub/irs-pdf/f1040.pdf")
