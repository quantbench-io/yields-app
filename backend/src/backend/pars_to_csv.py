import re, time

import pandas as pd
import sqlite3 as sql

from pathlib import Path
from urllib.parse import urlencode

# this is basically all the functions, but okay for now
from get_pars import (
    get_pars,
    get_latest_pars,
    get_pars_xml,
    parse_pars
)

# =====================================
# helper functions
def series_dict_to_table(D: dict) -> list:
    """
    Takes a dictionary of 'time series' and returns rows with [key, ...data]
    :param D:
        Dictionary of shape
        {k0: [(x00,y00),...], k1:[(x10,y10),...], ...}
    :return:
        List
        [[k0,y00,y01...], [k1,y10,y11], ...]
    """
    table = []
    for key, value in D.items():
      table.append([key, *[x[1] for x in value]])
    return table

def table_to_csv_str(table: list[list]) -> str :
    """
    Takes 'table' of Lists
        [L1, L2, ...]
    makes `,`-separated strings of the L_i's respective entries,
    and then concatenates these `,`-separated strings with newline `\n` separators
    """
    rows = [",".join(map(str,row)) for row in table]
    return "\n".join(rows)


# =====================================
# MAIN
# =====================================
def main():
    xml_dir = Path("/Users/taylor/yields-app/data/xml")
    csv_dir = Path("/Users/taylor/yields-app/data/csv")

    headers = [
        "date",
        "1M", "2M", "3M", "4M", "6M",
        "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"
    ]

    years = list(range(2020, 2027));

    for year in years:
        xml = get_pars_xml(year, mode="year")

        with open(xml_dir/f"pars{year}.xml", "w") as file:
            file.write(xml)

        pars = parse_pars(xml)

        pars_table = series_dict_to_table(pars)
        try:
            assert all(len(row) == len(headers) for row in pars_table)
        except:
            print(f"year {year} has different lengths")
            continue

        df = pd.DataFrame(pars_table, columns=headers)
        df.to_csv(csv_dir/f"pars{year}.csv", index=False)

        print(f"Done with {year}")

    return 0

if __name__ == "__main__":
    main()