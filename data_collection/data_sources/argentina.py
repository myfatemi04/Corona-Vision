import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait
from datetime import date, datetime, timedelta

lastDatapointsUpdate = 0
name = "Argentina"

def import_data() -> None:
    global lastDatapointsUpdate

    # use argentina date
    ar_time = datetime.now() + timedelta(hours=-3)
    ar_date = ar_time.date()

    urlv = ar_date.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-vespertino-covid-19.pdf")
    urlm = ar_date.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-matutino-covid-19.pdf")
    
    rq_evening = requests.get(urlv)
    if rq_evening.status_code == 200:
        import_pdf(rq_evening.content, ar_date)
    else:
        print(f"\r{rq_evening.status_code} on evening report download")
        rq_morning = requests.get(urlm)
        if rq_morning.status_code == 200:
            import_pdf(rq_morning.content, ar_date)
        else:
            print(f"\r{rq_morning.status_code} on morning report download")

# def import_historical_data() -> None:
#     # use argentina date
#     ar_date = date(2020, 3, 3)

#     urlv = ar_date.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-vespertino-covid-19.pdf")
#     urlm = ar_date.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-matutino-covid-19.pdf")
    
#     rq_evening = requests.get(urlv)
#     if rq_evening.status_code == 200:
#         import_pdf(rq_evening.content, ar_date)
#     else:
#         print("\rError on evening report download", end='\r')
#         rq_morning = requests.get(urlm)
#         if rq_morning.status_code == 200:
#             import_pdf(rq_morning.content, ar_date)
#         else:
#             print("\rError on morning report download", end='\r')

def expandObject(obj, depth=0):
    from PyPDF2.generic import IndirectObject
    if isinstance(obj, int) or isinstance(obj, str):
        print(depth * '\t', obj)
    elif isinstance(obj, list):
        for elem in obj:
            pre = '\t' * depth
            # print(f"{pre}{elem}")
            expandObject(elem, depth + 1)
    elif isinstance(obj, dict):
        for elem in obj:
            if elem != '/Parent':
                pre = '\t' * depth
                print(f"{pre}{elem}")
                expandObject(obj[elem], depth + 1)
    elif isinstance(obj, IndirectObject):
        expandObject(obj.getObject(), depth)

def import_pdf(content: bytes, entry_date: date) -> None:
    from io import BytesIO
    from PyPDF2 import PdfFileReader
    from PyPDF2.pdf import ContentStream
    import re
    global lastDatapointsUpdate
    bytesio = BytesIO(content)
    reader = PdfFileReader(bytesio)
    firstPage = reader.getPage(0)
    secondPage = reader.getPage(1)
    i = 0
    datapoints = []

    tokens = re.split(r'\s+', firstPage.extractText() + '\n' + secondPage.extractText())
    while i < len(tokens):
        if tokens[i] == '-':
            i = i + 1
            provinceTokens = []
            while not tokens[i].isdigit():
                provinceTokens.append(tokens[i])
                i += 1
            province = ' '.join(provinceTokens)
            i = i + 1
            if tokens[i] != '/':
                i += 1
                continue
            else:
                i += 1
            total = int(tokens[i].replace("*", ""))
            datapoints.append({
                'country': 'Argentina',
                'province': province,
                'total': total,
                'entry_date': entry_date
            })
        else:
            if len(datapoints) > 0:
                break
        
        i = i + 1

    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()