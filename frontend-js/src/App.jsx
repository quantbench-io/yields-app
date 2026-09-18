import {useState, useEffect} from "react";
import Plot from "react-plotly.js";
import './App.css'
import {CSVButton, TodayButton} from "./ExtraButtons.jsx";

const API_BASE_URL = "http://localhost:3000";
const YIELDCURVE = "/api/v1/yieldcurve/";

async function fetchYields(date) {
//   const url = new URL(YIELDCURVE+date, API_BASE_URL);
  const res = await fetch(API_BASE_URL+YIELDCURVE+`${date}`);
  return res.json();
}

export default function App() {
  const [date, setDate] = useState("2024-11-18");
  const [draft, setDraft] = useState(date);

  const [parNodes, setParNodes] = useState([]);
  const [parPlots, setParPlots] = useState({x:[], y:[]});

  const [priceNodes, setPriceNodes] = useState([]);

  const [zeroNodes, setZeroNodes] = useState([]);
  const [zeroPlots, setZeroPlots] = useState({x:[], y:[]});

  const [titleText, setTitleText] = useState(date);

  function unzipTimeSeries(seriesData) {
    const data = {
      x: seriesData.map(([t])=>12.0*t), // year-fraction to integer months
      y: seriesData.map(([,r])=>r)
    };
    return data;
  }

  useEffect(() => {
    fetchYields(date).then((body) => {
      console.log(body);

      setParNodes(body.parNodes);
      setParPlots(body.parPlots);

      setPriceNodes(body.priceNodes);

      setZeroNodes(body.zeroNodes);
      setZeroPlots(body.zeroPlots);

      setTitleText(body.date);

      return [body.parPlots, body.zeroPlots];
    })
      .then(([_parPlots,_zeroPlots]) => {
        // to make sure they use the updated values
        setParPlots(unzipTimeSeries(_parPlots));
        setZeroPlots(unzipTimeSeries(_zeroPlots));
      });
  }, [date]);

  function handleSubmit(e) {
    e.preventDefault();
    setDate(draft);
  }

  const plotData = [
    {...parPlots, type: "scatter", name: "Pars (Lin-Int)"},
    {...zeroPlots, type: "scatter", name: "Zeros (Log-Int)"},
  ];

  const saveData = [
      ["TauData", "parYields", "priceFactors", "ZeroRates"],
      ...(parNodes.map(([t,R],i)=>[t, R, priceNodes[i][1], zeroNodes[i][1]]))
  ];

  const layoutData = {
    title: {text: titleText},
  };

  const configData = {
    modeBarButtonsToRemove: ['lasso2d', 'autoScale2d', 'toImage', 'sendChartToCloud'],
    displaylogo: false,
  };

  return (
    <div style={{marginTop: "30px", display:"flex", flexDirection:"column", gap:"30px"}}>
      <div>
        <form onSubmit={handleSubmit}>
          <input type="text" value={draft} onChange={e => setDraft(e.currentTarget.value)} style={{width: "100px"}} />

          <button type="submit" style={{marginRight: "0px"}}>Submit</button>
          <TodayButton
            setDraft={setDraft}
            setDate={setDate}
            setTitleText={setTitleText}
            setParPlots={setParPlots}
            setZeroPlots={setZeroPlots}
          />
          <CSVButton data={saveData} fileName={`yields-${titleText}.csv`} />
        </form>
      </div>
      <Plot data={plotData} layout={layoutData} config={configData}/>
    </div>
  );
} //App