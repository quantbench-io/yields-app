# yields-app

—-

Before building the app, run

```
% cd frontend
% npm install
```

as the folder `frontend/dist` is built into the docker image. You can build and start the container with

```
./build-and-run-docker-image.sh
```

will both build the necessary container that has `frontend` and `backend` together, and expose the right port.

The backend reads data from `/backend/data/par_yields_all.db` using SQLite3 unless you use the "Get Latest" button, in which case it pulls the latest month's data and gives whatever the most recent trading day's data is.

I worked on this using Vite+React inside JetBrains Pycharm+Webstorm (for the backend and frontend, resp.). This recreated the graph from the assignment brief, as well as successfully pulled data from TreasuryDirect.gov and the database mentioned (it looks up if it already has the data before trying). I wrote the frontend in Typescript (will upload Friday) and only at the last minute duplicated a JS-only version to hopefully resolve the following bug...

#### A Note/in-progress investigation:

Something quite strange may occur upon building the docker image and running the entire app out of the container... the returned data seems to drop two of the time series points, wildly altering the shape of the graph.

Thus, if the zero curve looks odd, try running the backend and frontend separately:

```
% cd backend 
% ./docker-entrypoint.sh
```

```
% cd frontend
% npm install && npm run dev
```

and connecting to the port shown there (should be `localhost:5179`)