
export function CSVButton({data, fileName}) {
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



export function TodayButton(
    {setDraft, setDate, setTitleText, setParPlotNodes, setZeroPlotLogs}
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