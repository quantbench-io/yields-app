export default function TodayButton({setDraft,setDate}: {
    setDraft: (d: string) => void;
    setDate: (d: string) => void
}) {
    function handleClick() {
        const today = new Date().toISOString().slice(0, 10);
        setDraft(today);
        setDate(today);
        console.log(today);
    }
    return <button onClick={handleClick}>Get Latest</button>;
}