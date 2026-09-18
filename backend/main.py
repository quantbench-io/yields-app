import os, time, asyncio
from src.backend.tools import *
from src.backend.get_pars import *

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

static_html_path = os.getenv("STATIC_HTML_PATH") or "../frontend-js/dist"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.frontend("/", directory=static_html_path)

# a temporary wrapper for the different datasets;
def compute_zero_curve(date, par_data):
    if par_data == []:
        data = {
            "date": f"{date} does not have data.",
            "parNodes": [],
            "parPlots": [],
            "priceNodes": [],
            "zeroNodes": [],
            "zeroPlots": []
        }
        return data

    # some dates don't have values for every maturity, and have
    #   (tau, None)
    # instead. We don't use these in the interpolation.
    par_nodes = [x for x in par_data if x[1] is not None]

    R_nodes, R_t, P_nodes, Z_nodes, Z_t = zeros_from_par_nodes(par_nodes, freq=2)

    data = {
        "date": date,
        "parNodes": R_nodes,
        "parPlots": R_t,
        "priceNodes": P_nodes,
        "zeroNodes": Z_nodes,
        "zeroPlots": Z_t
    }

    assert len(data["parNodes"]) == len(data["priceNodes"]), "Mismatched price data length"
    assert len(data["parNodes"]) == len(data["zeroNodes"]), "Mismatched zeros data length"

    return data

# For testing
def pprint(dic):
    print(f"date: {dic['date']}")
    print("R \t\t\t\t\t P \t\t\t\t\t Z")
    print("===============================")
    for i in range(len(dic['parNodes'])) :
        tR, R = dic['parNodes'][i]
        tP, P = dic['priceNodes'][i]
        tZ, Z = dic['zeroNodes'][i]

        print(f"({tR:.3f}, {R:.3f}), \t\t\t ({tP:.3f}, {P:.3f}), \t\t\t ({tZ:.3f}, {Z:.3f})")

# ===============================================
@app.get("/api/v1/yieldcurve/{date}")
async def yield_curve(date: str):
    if date=="latest" :
        latest_date, par_data = get_latest_pars()
        return compute_zero_curve(latest_date, par_data)
    else :
        par_data = get_pars(date)
        return compute_zero_curve(date, par_data)