# yields-app-js

—-

You can build and start the container with

```
./dockerscript.sh
```

The backend reads data from `/backend/data/par_yields_all.db` using SQLite3 unless you use the "Get Latest" button, in which case it pulls the latest month's data and gives whatever the most recent trading day's data is.

I worked on this using Vite+React inside JetBrains Pycharm+Webstorm (for the backend and frontend, resp.). This recreated the graph from the assignment brief, as well as successfully pulled data from TreasuryDirect.gov and the database mentioned (it looks up if it already has the data before trying). 