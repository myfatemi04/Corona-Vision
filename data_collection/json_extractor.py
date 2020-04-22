from datetime import date, timedelta, datetime
import standards

def number(string):
    if type(string) == float or type(string) == int:
        return string
    string = string.strip()
    if not string:
        return 0
    string = string.split()[0]
    number = string.replace(",", "").replace("+", "").replace(".", "").replace("*", "")
    try:
        return int(number)
    except:
        return 0

def date_t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

json_methods = {
    "::unixtime": lambda x: datetime.utcfromtimestamp(x//1000).strftime("%Y-%m-%d"),
    "::number": lambda x: number(x),
    "::text": lambda x: x.text,
    "::strip": lambda x: x.strip(),
    "::cap": lambda x: x.capitalize(),
    "::dmy": lambda x: datetime.strptime(x, "%d%m%Y").strftime("%Y-%m-%d"),
    "::ymd": lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"),
    "::date_t": date_t,
    "::us_state_code": lambda x: standards.get_admin1_name("United States", x),
    "::str": lambda x: str(x)
}

def find_json(head, selectors):
    try:
        if type(selectors) != list:
            return selectors
        for selector in selectors:
            if selector.startswith("::"):
                head = json_methods[selector](head)
            else:
                head = head[selector]
        return head
    except KeyError:
        return None

def extract_json_row(row, labels):
    result = {}
    for label in labels:
        j = find_json(row, labels[label])
        if j is not None:
            result[label] = j
    return result