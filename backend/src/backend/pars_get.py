import re, time, json, requests
from urllib.parse import urlencode

# ===============================================
BASE_URL = "https://home.treasury.gov"
ENDPOINT = "/resource-center/data-chart-center/interest-rates/pages/xml"

# list of maturities we want
months = [1,2,3,4,6];
years = [1,2,3,5,7,10,20,30];
MATURITIES = [ (i/12, f"{i}MONTH") for i in months ]
MATURITIES.extend([ (1.0*i, f"{i}YEAR") for i in years ])

# ===============================================
def get_pars_xml(date: int, mode="month"):

    if mode=="month":
        params = urlencode({
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value_month": date
        })
    if mode=="year":
        params = urlencode({
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value": date
        })

    url = f"{BASE_URL}{ENDPOINT}?{params}"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.content.decode()


# =====================================
def parse_pars(xml: str):
    PROPS_ALL=re.findall(r"<m:properties>(.*?)</m:properties>", xml, re.S)

    PARS={}
    for prop_str in PROPS_ALL:
        # get the date
        match = re.search(r"<d:NEW_DATE.*?>(?P<date>[\d-]+)T(?P<time>[\d:]+)</d:NEW_DATE>", prop_str)
        date = match.group("date") if match is not None else None

        # get the time series
        _pars = []
        for t, mat in MATURITIES:
            match = re.search(r"<d:BC_"+mat+r".*?>(?P<yield>\d*\.?\d*)</d:BC_"+mat+r">", prop_str)
            y_par = float(match.group("yield")) if match is not None else None
            _pars.append((t, y_par))
        PARS[date] = _pars

    return PARS

# =====================================
def get_pars(date: str):
    _m = re.search(r"(\d{4})-(\d{2})", date)
    yyyymm = _m.group(1)+_m.group(2)

    # XML = get_pars_xml(yyyymm)
    with open("misc/pars202411.txt",'r') as file:
        XML = file.read()
    pars_data = parse_pars(XML)

    return pars_data.get(date, [])

# =====================================
def get_latest_pars():
    yyyymm = time.strftime("%Y%m", time.gmtime())
    XML = get_pars_xml(yyyymm)

    pars_data = parse_pars(XML)
    latest = max(pars_data.keys())

    return latest, pars_data.get(latest, [])