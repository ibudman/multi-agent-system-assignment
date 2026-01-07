import {useRef, useState} from "react";
import {LearningForm} from "./components/LearningForm";
import {ResultsTables} from "./components/ResultsTables";
import {Warnings} from "./components/Warnings";
import type {LearningPathsRequest, LearningPathsResponse} from "./types";
import {fetchLearningPaths} from "./api/learningPaths";

type Status = "idle" | "loading" | "done" | "error";

export default function App() {
    const [status, setStatus] = useState<Status>("idle");
    const [data, setData] = useState<LearningPathsResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const abortRef = useRef<AbortController | null>(null);

    async function handleSubmit(payload: LearningPathsRequest) {
        console.log("REQUEST payload:", payload);

        setStatus("loading");
        setError(null);

        abortRef.current?.abort();
        const controller = new AbortController();
        abortRef.current = controller;

        try {
            const resp = await fetchLearningPaths(payload, controller.signal);
            setData(resp);
            setStatus("done");
        } catch (e: any) {
            setError(e?.message ?? "Unknown error");
            setStatus("error");
        }
    }

    return (
        <div style={{padding: 24, fontFamily: "system-ui, Arial"}}>
            <h1>Learning Path Explorer</h1>

            <LearningForm onSubmit={handleSubmit} disabled={status === "loading"}/>
            
            <div style={{marginTop: 12, color: "#555"}}>
                {status === "idle" && (
                    <div>Enter a learning goal and optional preferences to begin.</div>
                )}

                {status === "loading" && (
                    <div>Searching, extracting, and organizing learning paths…</div>
                )}

                {status === "error" && (
                    <div style={{color: "crimson"}}>
                        Something went wrong. {error}
                    </div>
                )}
            </div>


            {data && (
                <div style={{marginTop: 12}}>
                    <div style={{color: "#555", fontSize: 12}}>request_id: {data.request_id}</div>
                    <Warnings warnings={data.warnings}/>
                    <ResultsTables results={data.results}/>
                </div>
            )}
        </div>
    );
}
