import {useState, useEffect} from "react";
import Plot from "react-plotly.js";

const API_BASE_URL = "http://localhost:8000";
const TIMESERIES_ENDPOINT = "/api/v1/yieldcurve/";

type TimeSeriesResponse = {
    date: string;
    pars: [number, number][];
    zeros: [number, number][];
};

async function fetchPars(dateStr: string) : Promise<TimeSeriesResponse> {
    const url = new URL(TIMESERIES_ENDPOINT+dateStr, API_BASE_URL);
    // url.searchParams.set("date", dateStr);
    const res = await fetch(url);
    return res.json();
}

export default function App() {
    const [date, setDate] = useState("2024-11-19");
    const [draft, setDraft] = useState(date);
    const [parsData, setParsData] = useState({x:[], y:[], type:"scatter"});
    const [zerosData, setZerosData] = useState({x:[], y:[], type:"scatter"});
    const [titleText, setTitleText] = useState(date);

    function getSeries(seriesData) {
        const data = {
            x: seriesData.map(([t])=>12.0*t),
            y: seriesData.map(([,r])=>r),
            type:"scatter"
        };
        console.log(data);
        return data;
    }

    useEffect(() => {
        fetchPars(date).then((body) => {
            console.log(body);
            setParsData(getSeries(body.pars));
            setZerosData(getSeries(body.zeros));
            setTitleText(body.date);
        });
    }, [date]);

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setDate(draft);
    }

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input type="text" value={draft} onChange={e => setDraft(e.currentTarget.value)} />
                <button type="submit">Submit</button>
            </form>
            <Plot data={[parsData,zerosData]} layout={{title:{text:titleText}}} />
        </div>
    );
}


// ========================================
// function getSeries(parsData) {
//     const ser = {
//         x: parsData.map(([t])=>t),
//         y: parsData.map(([,r])=>r),
//         type:"scatter"
//     };
//     return [ser];
// }
//
// useEffect(() => {
//     fetchPars().then((body) => {
//         setLayout({title: {text: body.date}});
//         setData(getSeries(body.pars));
//     });
// }, [date]);