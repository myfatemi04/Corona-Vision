def get_defaults():
    from datetime import datetime
    return {
        "location": {
            "admin0": "",
            "admin1": "",
            "admin2": ""
        },
        "datapoint": {
            "admin0": "",
            "admin1": "",
            "admin2": "",
            "entry_date": datetime.utcnow().date()
        }
    }