import {useState, useEffect} from "react";
import Plot from "react-plotly.js";
import CSVButton from "./CSVButton.tsx";
// import TodayButton from "./TodayButton.tsx";


const API_BASE_URL = "http://localhost:8000";
const YIELDCURVE_ENDPOINT = "/api/v1/yieldcurve/";

type TimeSeries = [number,number][];
type PlotSeries = {x: number[], y: number[]};

type TimeSeriesResponse = {
    date: string,
    parNodes: TimeSeries,
    discountNodes: TimeSeries,
    zeroNodes: TimeSeries,
    zeroLogs: TimeSeries,
};


async function fetchPars(dateStr: string) : Promise<TimeSeriesResponse> {
    const url = new URL(YIELDCURVE_ENDPOINT+dateStr, API_BASE_URL);
    const res = await fetch(url);
    return res.json();
}


function TodayButton({setDraft,setDate}) {
    function handleClick() {
        setDraft("latest");
        setDate("latest");
    }
    return <button onClick={handleClick}>Get Latest</button>;
}

export default function App() {
    const [date, setDate] = useState("2024-11-18");
    const [draft, setDraft] = useState(date);
    // const [latest, setLatest] = useState(false);

    const [parNodes, setParNodes] = useState<TimeSeries>([]);
    const [discountNodes, setDiscountNodes] = useState<TimeSeries>([]);
    const [zeroNodes, setZeroNodes] = useState<TimeSeries>([]);
    const [zeroLogs, setZeroLogs] = useState<TimeSeries>([]);

    const [parPlotNodes, setParPlotNodes] = useState<PlotSeries>({x:[], y:[]});
    const [zeroPlotLogs, setZeroPlotLogs] = useState<PlotSeries>({x:[], y:[]});

    const [titleText, setTitleText] = useState(date);

    // for 'unzipping' a TimeSeries
    function getSeries(seriesData: TimeSeries) {
        const data = {
            x: seriesData.map(([t])=>12.0*t),
            y: seriesData.map(([,r])=>r)
        };
        return data;
    }

    useEffect(() => {
        fetchPars(date).then((body) => {
            console.log(body);

            setParNodes(body.parNodes);
            setDiscountNodes(body.discountNodes);
            setZeroNodes(body.zeroNodes);
            setZeroLogs(body.zeroLogs);
            setTitleText(body.date);

            return [body.parNodes, body.zeroLogs];
        })
        .then(([_parNodes,_zeroLogs]) => {
            // to make sure they use the updated values
            setParPlotNodes(getSeries(_parNodes));
            setZeroPlotLogs(getSeries(_zeroLogs));
        });
    }, [date]);

    function handleSubmit(e: React.SubmitEvent) {
        e.preventDefault();
        setDate(draft);
    }

    // function handleGetLatest(e: React.SubmitEvent) {
    //     e.preventDefault();
    //     const today = new Date().toISOString().slice(0, 10);
    //     setDraft(today);
    //     setDate(today);
    // }

    const plotData = [
        {...parPlotNodes, type: "scatter", name: "Par Yields (Lin-Int)"},
        {...zeroPlotLogs, type: "scatter", name: "Zeros (Log-Int)"},
    ];

    const saveData = [
        ["TauData", "ParYields", "DiscountFactors", "ZeroRates"],
        ...(parNodes.map(([t,r],i)=>[t, r, discountNodes[i][1], zeroNodes[i][1]]))
    ];

    return (
        <div style={{marginTop: "30px", display:"flex", flexDirection:"column", gap:"30px"}}>
        <div>
            <form onSubmit={handleSubmit}>
                <input type="text" value={draft} onChange={e => setDraft(e.currentTarget.value)} style={{width: "100px"}} />
                <button type="submit" style={{marginRight: "10px"}}>Submit</button>
                <TodayButton setDraft={setDraft} setDate={setDate} />
                <CSVButton data={saveData} fileName="scratch.csv" />
            </form>
        </div>
        <Plot data={plotData} layout={{title:{text:titleText}}} />
        </div>
    );
}


// ==========================