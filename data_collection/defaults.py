def get_defaults():
    from datetime import datetime
    return {
        "location": {
            "country": "",
            "admin1": "",
            "county": ""
        },
        "datapoint": {
            "country": "",
            "admin1": "",
            "county": "",
            "entry_date": datetime.utcnow().date()
        }
    }