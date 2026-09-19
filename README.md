# yields-app-js

A simple web-page that uses the published *par-yields* of (U.S.) Treasury securities to "bootstrap" the *yield-curve* of monthly *zero-rates* (that is, to price *zero-coupon bonds*) for a range of maturities. 

The backend is a Python FastAPI server that pulls and processes daily Treasury yield curve data, either fresh from `TreasuryDirect.gov`'s yield curve XML feeds, or from the SQLite3 database `/backend/data/par-yields-all.db`. The frontend (in `frontend-ts`) plots the interpolated yield curve, and allows users to select and save the computed curve data for historical dates. The app's main page also documents the necessary definitions and math used in our computations.

The entire app may be built and started in a Docker container using
```sh
build-start.sh
```

#### Repo Structure
```
yields-app/
├─ backend/
│  ├─ data/
│  └─ src/backend/
├─ frontend-js/ # JS/JSX-only version
├─ frontend-ts/ # primary frontend
└─ misc/ 
```

<!-- <img style="display: block; margin-left: auto; margin-right: auto; margin-top: 0; margin-bottom: 0;scale: 60%; border: 5px solid #365687; max-width: 800px; max-height:600px"  src='misc/hurdle.png'/> -->