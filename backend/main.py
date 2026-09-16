import os, time, asyncio
from src.backend.tools import *
from src.backend.get_pars import *

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

static_html_path = os.getenv("STATIC_HTML_PATH") or "../frontend/dist"

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
        _data = {
            "date": f"{date} does not have data.",
            "parNodes": [],
            "discountNodes": [],
            "zeroNodes": [],
            "zeroLogs": []
        }
        return _data

    # some dates don't have values for every maturity, and have
    #   (tau, None)
    # instead. We don't want to use those in the interpolation, so we drop.
    par_nodes = [x for x in par_data if x[1] is not None]
    D_nodes, Z_nodes, Z_log = zeros_from_par_nodes(par_nodes, freq=2)

    _data = {
        "date": date,
        "parNodes": par_nodes,
        "discountNodes": D_nodes,
        "zeroNodes": Z_nodes,
        "zeroLogs": Z_log
    }

    return _data

# ===============================================
@app.get("/api/v1/yieldcurve/{date}")
async def get_yield_curve(date: str):
    if date=="latest" :
        latest_date, par_data = get_latest_pars()
        return compute_zero_curve(latest_date, par_data)
    else :
        par_data = get_pars(date)
        return compute_zero_curve(date, par_data)