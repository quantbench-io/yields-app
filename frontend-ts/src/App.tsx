import {useState, useEffect} from "react";
import Plot from "react-plotly.js";
import './App.css';
import {CSVButton, TodayButton} from "./ExtraButtons.tsx";

const API_BASE_URL = "http://localhost:3000";
const YIELDCURVE = "/api/v1/yieldcurve/";

type TimeSeries = [number,number][];
type PlotSeries = {x: number[], y: number[]};

type TimeSeriesResponse = {
    date: string,
    parNodes: TimeSeries,
    parPlots: TimeSeries,
    priceNodes: TimeSeries,
    zeroNodes: TimeSeries,
    zeroPlots: TimeSeries,
};

async function fetchYields(date: string) : Promise<TimeSeriesResponse> {
    // const url = new URL(YIELDCURVE+date, API_BASE_URL);
    const res = await fetch(API_BASE_URL+YIELDCURVE+`${date}`);
    return res.json();
}

export default function App() {
    const [date, setDate] = useState("2024-11-18");
    const [draft, setDraft] = useState(date);

    const [parNodes, setParNodes] = useState<TimeSeries>([]);
    const [parPlots, setParPlots] = useState<PlotSeries>({x:[], y:[]});

    const [priceNodes, setPriceNodes] = useState<TimeSeries>([]);

    const [zeroNodes, setZeroNodes] = useState<TimeSeries>([]);
    const [zeroPlots, setZeroPlots] = useState<PlotSeries>({x:[], y:[]});

    const [titleText, setTitleText] = useState(date);

    function unzipTimeSeries(seriesData: TimeSeries) {
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
            setPriceNodes(body.priceNodes);
            setZeroNodes(body.zeroNodes);

            // setParPlots(body.parPlots);
            // setZeroPlots(body.zeroPlots);

            setTitleText(body.date);

            return [body.parPlots, body.zeroPlots];
        })
        .then(([_parPlots,_zeroPlots]) => {
            // to make sure they use the updated values
            setParPlots(unzipTimeSeries(_parPlots));
            setZeroPlots(unzipTimeSeries(_zeroPlots));
        });
    }, [date]);

    function handleSubmit(e: React.SubmitEvent) {
        e.preventDefault();
        setDate(draft);
    }

    const plotData = [
        {...parPlots, type: "scatter", name: "Pars (Lin-Int)"},
        {...zeroPlots, type: "scatter", name: "Zeros (Log-Int)"},
    ];

    const saveData = [
        ["tauData", "parYields", "priceFactors", "zeroRates"],
        ...(parNodes.map(([t,R],i)=>[t, R, priceNodes[i][1], zeroNodes[i][1]]))
    ];

    // const saveData = [
    //     ["TauData", "ZeroRates"],
    //     ...zeroNodes
    // ];

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
        <Plot data={plotData} layout={layoutData} config={configData} />
        </div>
    );
} //App