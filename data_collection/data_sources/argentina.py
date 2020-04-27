import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait
from datetime import date, datetime, timedelta

lastDatapointsUpdate = 0

def import_data() -> None:
    global lastDatapointsUpdate
    if time.time() - lastDatapointsUpdate < minWait:
        print("Not uploading Argentina because elapsed < minWait")
        return
    else:
        print("Loading from Argentina...")

    # use argentina date
    ar_time = datetime.now() + timedelta(hours=-3)
    ar_date = ar_time.date()

    urlv = ar_date.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-vespertino-covid-19.pdf")
    urlm = ar_date.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-matutino-covid-19.pdf")
    
    rq_evening = requests.get(urlv)
    if rq_evening.status_code == 200:
        import_pdf(rq_evening.content, ar_date)
    else:
        print("\rError on evening report download", end='\r')
        rq_morning = requests.get(urlm)
        if rq_morning.status_code == 200:
            import_pdf(rq_morning.content, ar_date)
        else:
            print("\rError on morning report download", end='\r')

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

def import_pdf(content: bytes, entry_date: date) -> None:
    from io import BytesIO
    from PyPDF2 import PdfFileReader
    global lastDatapointsUpdate
    bytesio = BytesIO(content)
    reader = PdfFileReader(bytesio)
    secondPage = reader.getPage(1)
    lines = secondPage.extractText().split("\n")
    i = 0
    datapoints = []
    while i < len(lines):
        if lines[i] == '-':
            # provinceLine = "Buenos Aires [number of daily cases]"
            provinceLine = lines[i + 2].strip()
            total = int(lines[i + 5].replace("*", "").strip())
            lastSpace = provinceLine.rfind(" ")
            province = provinceLine[:lastSpace]
            datapoints.append({
                'country': 'Argentina',
                'province': province,
                'total': total,
                'entry_date': entry_date
            })
            i += 7
        else:
            if len(datapoints) > 0:
                break
            else:
                i += 1

    if upload.upload_datapoints(datapoints, "https://www.argentina.gob.ar/coronavirus/informe-diario"):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()