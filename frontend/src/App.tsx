import {useState} from "react";
import {LearningForm} from "./components/LearningForm";
import {ResultsTables} from "./components/ResultsTables";
import {Warnings} from "./components/Warnings";
import type {LearningPathsRequest, LearningPathsResponse} from "./types";
import {mockLearningPathsResponse} from "./mockResponse";

type Status = "idle" | "loading" | "done";

export default function App() {
    const [status, setStatus] = useState<Status>("idle");
    const [data, setData] = useState<LearningPathsResponse | null>(null);

    function handleSubmit(payload: LearningPathsRequest) {
        console.log("REQUEST payload:", payload);

        setStatus("loading");
        setData(null);

        setTimeout(() => {
            setData(mockLearningPathsResponse);
            setStatus("done");
        }, 800);
    }

    return (
        <div style={{padding: 24, fontFamily: "system-ui, Arial"}}>
            <h1>Learning Path Explorer</h1>

            <LearningForm onSubmit={handleSubmit} disabled={status === "loading"}/>

            <div style={{marginTop: 12}}>
                <div style={{fontWeight: 600}}>Status</div>
                <div>{status === "loading" ? "Loading…" : status === "done" ? "Done" : "Idle"}</div>
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
