import os, asyncio
from random import randint, Random
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


# ===============================================
@app.get("/api/v1/scores/{maximum}")
async def get_scores(maximum: int) -> list[float]:
    result = []
    random = Random()
    for i in range(1, max(100, maximum)):
        result.append(random.uniform(0,1))
    return result


# ===============================================
@app.get("/api/v1/yieldcurve/{date}")
async def get_yield_curve(date: str):
    par_yields = get_pars(date)
    if par_yields == [] :
        return {"date": f"{date} does not have data.", "pars": [], "zeros": []}

    R_t, D_t = bootstrap_D_from_par_yields(par_yields, freq=2, returnR=True, percentize=True)

    _t = [t for t, _ in par_yields]
    D_nodes = [(t, d) for t, d in D_t if t in _t]
    D_log = log_interpolate_Dm(D_nodes)
    Z_log = D_to_Zc(D_log)
    Z_log = [(t,100*z) for t,z in Z_log] # to percent

    return {"date": date, "pars": par_yields, "zeros": Z_log}
