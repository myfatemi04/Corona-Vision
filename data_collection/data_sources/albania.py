import requests
import json_extractor

def import_data():
    rq = requests.get('https://coronavirus.al/api/qarqet.php')
    j = rq.json()
    dp = {
        'total': json_extractor.column_total(j, 'raste_gjithsej')
    }
    print(dp)

import_data()