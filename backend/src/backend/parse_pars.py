
# =====================================
def parse_props(prop_str):
  # get the date
  match = re.search(r"<d:NEW_DATE.*?>(.*?)</d:NEW_DATE>", prop_str)
  date = match.group(1) if match is not None else None

  # get the pars
  pars = {}
  for mat in maturity_strs:
    match = re.search(r"<d:BC_"+mat+r".*?>(?P<yield>\d*\.\d*)</d:BC_"+mat+r">", prop_str)
    y_par = float(match.group(1)) if match is not None else None
    pars[mat] = y_par

  return {"date":date, "pars":pars}

# =====================================
# MAIN
# =====================================
def main():
  params=urlencode({
    "data": "daily_treasury_yield_curve",
    "field_tdr_date_value_month": str(202411)
  })
  url=f"{BASE_URL}{ENDPOINT}?{params}"

  response=requests.get(url, timeout=30)
  response.raise_for_status()

  XML=response.content.decode()
  with open('../../misc/test.txt', 'w') as file:
    file.write(XML)

  PROPS_ALL=re.findall(r"<m:properties>(.*?)</m:properties>", XML, re.S)

  PARS=[]
  for prop_str in PROPS_ALL:
    PARS.append(parse_props(prop_str))

  with open("../../misc/test_xml.json", 'w') as file:
    json.dump(PARS, file)

if __name__ == "__main__":
  main()