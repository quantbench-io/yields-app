import os, time, asyncio
from backend.tools import *
from backend.get_pars import *

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
def compute_zero_curve(date, par_yields):
    if par_yields == []:
        _data = {
            "date": f"{date} does not have data.",
            "parNodes": [],
            "discountNodes": [],
            "zeroNodes": [],
            "zeroLogs": []
        }
        return _data

    D_nodes, Z_nodes, Z_log = zeros_from_pars(par_yields, freq=2)

    _data = {
        "date": date,
        "parNodes": par_yields,
        "discountNodes": D_nodes,
        "zeroNodes": Z_nodes,
        "zeroLogs": Z_log
    }

    return _data

# ===============================================
@app.get("/api/v1/yieldcurve/{date}")
async def get_yield_curve(date: str):
    if date=="latest" :
        latest_date, par_yields = get_latest_pars()
        return compute_zero_curve(latest_date, par_yields)
    else :
        par_yields = get_pars(date)
        return compute_zero_curve(date, par_yields)