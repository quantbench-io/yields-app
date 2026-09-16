import {useState, useEffect} from "react";
import Plot from "react-plotly.js";
import './App.css'
import {CSVButton, TodayButton} from "./ExtraButtons.jsx";

const API_BASE_URL = "http://localhost:8000";
// const YIELDCURVE = "/api/v1/yieldcurve/";


async function fetchPars(date) {
//   const url = new URL(YIELDCURVE+date, API_BASE_URL);
  const res = await fetch(API_BASE_URL+`/api/v1/yieldcurve/${date}`);
  return res.json();
}


export default function App() {
  const [date, setDate] = useState("2024-11-18");
  const [draft, setDraft] = useState(date);
  // const [latest, setLatest] = useState(false);

  const [zeroNodes, setZeroNodes] = useState([]);

  const [parPlotNodes, setParPlotNodes] = useState({x:[], y:[]});
  const [zeroPlotLogs, setZeroPlotLogs] = useState({x:[], y:[]});

  const [titleText, setTitleText] = useState(date);

  function getSeries(seriesData) {
    const data = {
      x: seriesData.map(([t])=>12.0*t),
      y: seriesData.map(([,r])=>r)
    };
    return data;
  }

  useEffect(() => {
    fetchPars(date).then((body) => {
      console.log(body);

      // setParNodes(body.parNodes);
      // setDiscountNodes(body.discountNodes);
      setZeroNodes(body.zeroNodes);
      // setZeroLogs(body.zeroLogs);
      setTitleText(body.date);

      return [body.parNodes, body.zeroLogs];
    })
      .then(([_parNodes,_zeroLogs]) => {
        // to make sure they use the updated values
        setParPlotNodes(getSeries(_parNodes));
        setZeroPlotLogs(getSeries(_zeroLogs));
      });
  }, [date]);

  function handleSubmit(e) {
    e.preventDefault();
    setDate(draft);
  }

  const plotData = [
    {...parPlotNodes, type: "scatter", name: "Par Yields (Lin-Int)"},
    {...zeroPlotLogs, type: "scatter", name: "Zeros (Log-Int)"},
  ];

  // const saveData = [
  //     ["TauData", "ParYields", "DiscountFactors", "ZeroRates"],
  //     ...(parNodes.map(([t,r],i)=>[t, r, discountNodes?.[i]?.[1], zeroNodes?.[i]?.[1]]))
  // ];
  const saveData = [
    ["TauData", "ZeroRates"],
    ...zeroNodes
  ];

  return (
    <div style={{marginTop: "30px", display:"flex", flexDirection:"column", gap:"30px"}}>
      <div>
        <form onSubmit={handleSubmit}>
          <input type="text" value={draft} onChange={e => setDraft(e.currentTarget.value)} style={{width: "100px"}} />
          <button type="submit" style={{marginRight: "10px"}}>Submit</button>
          <TodayButton
            setDraft={setDraft}
            setDate={setDate}
            setTitleText={setTitleText}
            setParPlotNodes={setParPlotNodes}
            setZeroPlotLogs={setZeroPlotLogs}
          />
          <CSVButton data={saveData} fileName="scratch.csv" />
        </form>
      </div>
      <Plot data={plotData} layout={{title:{text:titleText}}} />
    </div>
  );
}


// ==========================