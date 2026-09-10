#!/usr/bin/env python
import pandas as pd
from pathlib import Path

# getting the project root
project_root = Path.cwd()
while (project_root.name != "backend") and (project_root.parent != project_root):
    project_root = project_root.parent

csv_dir = project_root / "data/csv"

def main():
    df_min = 1990
    df_max = 2026

    df = pd.read_csv(csv_dir/f"pars{df_min}.csv")
    for file in csv_dir.glob("*.csv"):

        # only get data in a certain year range
        if df_min < int(file.stem[-4:]) <= df_max :
            _df = pd.read_csv(file)
            df = pd.concat([df, _df], ignore_index=True)

    df.to_csv(project_root/data/"par_yields_all.csv", index=False)

if __name__ == "__main__":
    main()