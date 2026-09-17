type CSVButtonProps = {
    data: (number|string)[][];
    fileName?: string;
}

export function CSVButton({data, fileName}: CSVButtonProps) {
    const downloadCSV = () => {
        const csvString = data.map(row => row.join()).join("\n");
        const blob = new Blob([csvString], {type: 'text/csv'});
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = fileName || 'download.csv';
        link.click();

        URL.revokeObjectURL(url);
    };
    return <button onClick={downloadCSV}>Export CSV</button>;
}


type TodayButtonProps = {
    setDraft: (s: string) => void;
    setDate: (s: string) => void;
    setTitleText: (s: string) => void;
    setParPlotNodes: (ser: {x: number[], y: number[]}) => void;
    setZeroPlotLogs: (ser: {x: number[], y: number[]}) => void;
}

export function TodayButton(
    {setDraft, setDate, setTitleText, setParPlotNodes, setZeroPlotLogs}: TodayButtonProps
) {
    function handleClick() {
        setDraft("latest");
        setDate("latest");
        setTitleText("Retrieving...");
        setParPlotNodes({x:[], y:[]});
        setZeroPlotLogs({x:[], y:[]});
    }
    return <button onClick={handleClick}>Get Latest</button>;
}