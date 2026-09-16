import re
import xml.etree.ElementTree as ET

# list of maturities we want
months = [1,2,3,4,6]
years = [1,2,3,5,7,10,20,30]
mat_map = {f"BC_{i}MONTH" : 1.0*i/12 for i in months}
for y in years :
    mat_map[f"BC_{y}YEAR"] = 1.0*y

namespaces = {
    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
    '': 'http://www.w3.org/2005/Atom'
}

def pars_data_from_xml(xml_str: str, ns: dict):
    root = ET.fromstring(xml_str)

    entries = root.findall('entry', ns)

    entries_dict = dict()

    for entry in entries:
        prop = entry.find('./content/m:properties', ns)
        prop_dict = dict()

        for elem in prop:
            key = re.sub("{%s}"%ns['d'], "", elem.tag)
            if key != 'BC_30YEARDISPLAY':
                prop_dict[key] = (elem.attrib["{%s}type"%ns['m']], elem.text)

        date = prop_dict.pop('NEW_DATE')[1].removesuffix('T00:00:00')
        entries_dict[date] = prop_dict

    pars_data = dict()

    # returns a series of (tau, rate)
    for date, date_pars in entry_test.items():
        t_series = []
        for mat, tau in mat_map.items():
            datum = date_pars.get(mat)
            if datum is not None:
                t_series.append((tau, float(datum[1])))
            else:
                t_series.append((tau, None))

        pars_data[date] = t_series

    return pars_data