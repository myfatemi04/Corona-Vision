def get_defaults():
    from datetime import datetime
    return {
        "location": {
            "country": "",
            "province": "",
            "county": ""
        },
        "datapoint": {
            "country": "",
            "province": "",
            "county": "",
            "entry_date": datetime.utcnow().date()
        }
    }