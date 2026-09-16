import re, time, json, requests
import sqlite3 as sql
import os

from urllib.parse import urlencode

# ===============================================
BASE_URL = "https://home.treasury.gov"
ENDPOINT = "/resource-center/data-chart-center/interest-rates/pages/xml"
DB_FILE = "./data/par_yields_all.db"

# list of maturities we want
months = [1,2,3,4,6];
years = [1,2,3,5,7,10,20,30];
MATURITIES = [ (i/12, f"{i}MONTH") for i in months ]
MATURITIES.extend([ (1.0*i, f"{i}YEAR") for i in years ])
TAUS = [x[0] for x in MATURITIES]

# ===============================================
def get_pars_xml(date: str, mode="month"):

    # this is how Treasury wants date
    _m = re.search(r"(\d{4})-(\d{2})", date)
    yyyymm = _m.group(1)+_m.group(2)

    if mode=="month":
        params = urlencode({
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value_month": yyyymm
        })
    if mode=="year":
        yyyy = yyyymm[:-2]
        params = urlencode({
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value": yyyy
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
def lookup_par_ser_date(date:str, DB:str) -> list:
    conn = sql.connect(DB)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM par_yields_all WHERE \"date\" = \"{date}\";")

    fetched = cur.fetchall()

    cur.close()
    conn.close()

    if fetched == []:
        return []
    else:
        return list(zip(TAUS, fetched[0][1:]))

def more_than_a_week(date: str) -> bool:
    """
    True if now is >= 7 calendar days after the date given
    :param date:
        reference date
    :return:
        True if now is >= 7 calendar days after the date given
    """
    WEEK_SECS = 60*60*24*7.0
    now = time.localtime()
    today_secs = time.mktime(now) - 3600*now.tm_hour - 60*now.tm_min - now.tm_sec
    date_secs = time.mktime(time.strptime(date, "%Y-%m-%d"))

    return (today_secs - date_secs) > WEEK_SECS


# =====================================
def get_pars(date: str):

    print(os.getcwd())
    # check if DB_FILE has data for date
    pars_ser = lookup_par_ser_date(date, DB_FILE)

    # No published data for 2010-10-11, yet appears in Treasury files;
    # will drop this row from SQL table later
    if date=="2010-10-11" : return []


    if pars_ser != [] :
        return pars_ser

    # if there is no data and it's been 7 days,
    # conclude that the date wasn't a trading day
    elif more_than_a_week(date) :
        return []

    # otherwise, try to pull it down.
    # (no update DB function at the moment)
    else:
        xml = get_pars_xml(date, mode="month")
        pars_data = parse_pars(xml)

        return pars_data.get(date, [])

# =====================================
def get_latest_pars():
    """
    Tries to get today's data. Returns the most recently published data if today hasn't
    been published yet or today isn't a trading day.
    :return:
    """
    date = time.strftime("%Y-%m-%d", time.localtime())

    xml = get_pars_xml(date, mode="month")
    pars_data = parse_pars(xml)

    latest = max(pars_data.keys())

    return latest, pars_data.get(latest, [])