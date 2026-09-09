import re, json, requests
from urllib.parse import urlencode

# ===============================================
BASE_URL = "https://home.treasury.gov"
ENDPOINT = "/resource-center/data-chart-center/interest-rates/pages/xml"

# list of maturities we want
months = [1,2,3,4,6];
years = [1,2,3,5,7,10,20,30];
maturities = [ (i/12, f"{i}MONTH") for i in months ]
maturities.extend([ (1.0*i, f"{i}YEAR") for i in years ])


# ===============================================
def get_pars_xml(date: int):
    params = urlencode({
        "data": "daily_treasury_yield_curve",
        "field_tdr_date_value_month": str(date)
    })
    url = f"{BASE_URL}{ENDPOINT}?{params}"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.content.decode()

# =====================================
def parse_props(prop_str):
    _pars = []
    for t, mat in maturities:
        match = re.search(r"<d:BC_"+mat+r".*?>(?P<yield>\d*\.?\d*)</d:BC_"+mat+r">", prop_str)
        y_par = float(match.group("yield")) if match is not None else None
        _pars.append((t,y_par))

    return _pars
    # return {"date":date, "pars":pars}

# =====================================
def parse_pars(xml: str):
    PROPS_ALL=re.findall(r"<m:properties>(.*?)</m:properties>", xml, re.S)

    PARS={}
    for prop_str in PROPS_ALL:
        # get the date
        match = re.search(r"<d:NEW_DATE.*?>(?P<date>[\d-]+)T(?P<time>[\d:]+)</d:NEW_DATE>", prop_str)
        date = match.group("date") if match is not None else None

        # get the time series
        PARS[date] = parse_props(prop_str)
    return PARS

# =====================================
def get_pars(date: str):
    # XML = get_pars_xml(year_month)
    with open("misc/pars202411.txt",'r') as file:
        XML = file.read()
    pars_data = parse_pars(XML)
    return pars_data.get(date, [])


