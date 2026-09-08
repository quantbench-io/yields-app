import { useEffect, useState, useCallback } from "react";
import Plot from "react-plotly.js";
import './App.css'

// ============================================================
// 1. TYPES
// ============================================================
// FILL IN: match these to whatever your OpenAPI schema actually
// says the endpoint returns. Right now this assumes the response
// body looks something like: { "series": [[t0, r0], [t1, r1], ...] }
// Adjust freely — this is the one place that *must* match your
// server's real response shape.

type TimeSeriesTuple = [number, number]; // [t, r]

interface TimeSeriesResponse {
  series: TimeSeriesTuple[];
  // FILL IN: any other fields the endpoint returns (metadata, units, etc.)
}

// A friendlier "unpacked" shape for feeding straight into Plotly,
// which wants separate x[] and y[] arrays rather than [x,y] pairs.
interface UnpackedSeries {
  t: number[];
  r: number[];
}

// ============================================================
// 2. CONFIG — EDIT ME
// ============================================================
// GOTCHA: your Vite dev server and your API server run on DIFFERENT
// ports (e.g. Vite on :5173, your API on :8000). That means this is
// a cross-origin request, so your server needs CORS enabled for the
// Vite origin — otherwise the browser will silently block the
// response and you'll just see a network/console error. Alternatively,
// look into Vite's `server.proxy` config to sidestep CORS entirely
// during development.

const API_BASE_URL = "http://localhost:8000"; // FILL IN: your actual host:port
const TIMESERIES_ENDPOINT = "/api/timeseries"; // FILL IN: your actual OpenAPI path

// ============================================================
// 3. DATA FETCHING
// ============================================================
// This is written as a plain `fetch` call. If your server publishes
// an OpenAPI spec, you could later swap this out for a generated
// client (e.g. via `openapi-fetch` + `openapi-typescript`, which
// generates TS types straight from your spec) so you get autocomplete
// and compile-time checking on request/response shapes. Not necessary
// to start — plain fetch is fine while you're sketching things out.

async function fetchTimeSeries(
  dateStr: string,
  signal?: AbortSignal
): Promise<UnpackedSeries> {
  const url = new URL(TIMESERIES_ENDPOINT, API_BASE_URL);
  url.searchParams.set("date", dateStr); // GOTCHA: format must match what the server expects (e.g. "YYYY-MM-DD")

  const res = await fetch(url.toString(), { signal });

  if (!res.ok) {
    // FILL IN: real error handling / message extraction from the response body
    throw new Error(`Request failed: ${res.status}`);
  }

  const body: TimeSeriesResponse = await res.json();

  // Unpack [t, r] tuples into separate arrays for Plotly.
  const t: number[] = [];
  const r: number[] = [];
  for (const [tVal, rVal] of body.series) {
    t.push(tVal);
    r.push(rVal);
  }
  return { t, r };
}

// ============================================================
// 4. SUB-COMPONENTS (sketches only — feel free to split into
//    separate files once you're happy with how they behave)
// ============================================================

interface DateSelectorProps {
  value: string;
  onSubmit: (newDate: string) => void;
}

function DateSelector({ value, onSubmit }: DateSelectorProps) {
  // Local draft state, separate from the "committed" date that
  // actually triggers a fetch — lets you decide whether submitting
  // happens on every keystroke/change, or only on explicit submit.
  const [draft, setDraft] = useState(value);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit(draft);
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* GOTCHA: <input type="date"> gives you value strings already
          in "YYYY-MM-DD" format, which is convenient if your API
          expects ISO dates — one less thing to convert. */}
      <input
        type="date"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
      />
      <button type="submit">Load</button>
      {/* FILL IN: consider whether you *also* want onChange to
          auto-submit (no button needed) vs. requiring explicit submit.
          Both are valid product decisions — your call. */}
    </form>
  );
}

interface MathNotesProps {
  // FILL IN: shape this however your math-rendering library wants it —
  // e.g. a raw LaTeX string to hand to <BlockMath> from react-katex.
}

function MathNotes(_props: MathNotesProps) {
  return (
    <details>
      <summary>Notes</summary>
      <div>
        {/* FILL IN: rendered math + descriptive text go here, e.g.:
             <BlockMath math="r(t) = ..." />
           (* your descriptive text here *)
        */}
      </div>
    </details>
  );
}

// ============================================================
// 5. MAIN APP COMPONENT
// ============================================================

export default function App() {
  const [date, setDate] = useState<string>("2024-01-01"); // FILL IN: sensible default
  const [series, setSeries] = useState<UnpackedSeries>({ t: [], r: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback((dateStr: string) => {
    // GOTCHA: if the user changes the date quickly, an earlier
    // request could resolve AFTER a later one, overwriting fresh
    // data with stale data ("race condition"). AbortController
    // (used here) is the standard fix — cancel the previous
    // in-flight request when a new one starts.
    const controller = new AbortController();

    setLoading(true);
    setError(null);

    fetchTimeSeries(dateStr, controller.signal)
      .then(setSeries)
      .catch((err) => {
        if (err.name !== "AbortError") setError(String(err));
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  // Fetch on mount, and again any time `date` changes.
  useEffect(() => {
    const cancel = loadData(date);
    return cancel;
  }, [date, loadData]);

  return (
    <div>
      <h1>{/* (* your app title here *) */}</h1>

      <DateSelector value={date} onSubmit={setDate} />

      {loading && <p>Loading…</p>}
      {error && <p>Error: {error}</p>}

      <Plot
        data={[
          {
            x: series.t,
            y: series.r,
            type: "scatter",
            mode: "lines",
            // FILL IN: name, line color/style, etc.
          },
        ]}
        layout={{
          title: { text: "" } /* FILL IN */,
          xaxis: { title: { text: "t" } },
          yaxis: { title: { text: "r" } },
          // FILL IN: width/height, or make it responsive via `useResizeHandler`
        }}
      />

      <MathNotes />
    </div>
  );
}