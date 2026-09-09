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
BASE_URL = "https://home.treasury.gov"
ENDPOINT = "/resource-center/data-chart-center/interest-rates/pages/xml"

# list of maturities we want
months = [1,2,3,4,6];
years = [1,2,3,5,7,10,20,30];
maturity_strs = [ f"{i}MONTH" for i in months ]
maturity_strs.extend([ f"{i}YEAR" for i in years ])


# ===============================================
@app.get("/api/v1/scores/{maximum}")
async def get_scores(maximum: int) -> list[float]:
    result = []
    random = Random()
    for i in range(1, max(100, maximum)):
        result.append(random.uniform(0,1))
    return result


# ===============================================
@app.get("/api/v1/zeros/{date}")
async def get_zeros(date: int) -> list[float]:
    result = await get_pars(date)
    return result

#
# # =====================================
# # MAIN
# # =====================================
# def main():
#
#   with open('misc/test.txt', 'w') as file:
#     file.write(XML)
#
#   with open("misc/test_xml.json", 'w') as file:
#     json.dump(PARS, file)
#

