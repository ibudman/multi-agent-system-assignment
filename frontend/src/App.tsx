import {useRef, useState} from "react";
import {LearningForm} from "./components/LearningForm";
import {ResultsTables} from "./components/ResultsTables";
import {Warnings} from "./components/Warnings";
import {Spinner} from "./components/Spinner";
import type {LearningPathsRequest, LearningPathsResponse} from "./types";
import {fetchLearningPaths} from "./api/learningPaths";

type Status = "idle" | "loading" | "done" | "error";

export default function App() {
    const [status, setStatus] = useState<Status>("idle");
    const [data, setData] = useState<LearningPathsResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const abortRef = useRef<AbortController | null>(null);

    async function handleSubmit(payload: LearningPathsRequest) {
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
        <div style={{minHeight: "100vh", background: "#f6f7fb"}}>
            <div style={{maxWidth: 1100, margin: "0 auto", padding: "28px 18px"}}>
                <header style={{marginBottom: 14}}>
                    <h1 style={{margin: 0, fontSize: 28, letterSpacing: -0.3}}>
                        Learning Path Explorer
                    </h1>
                    <p style={{margin: "6px 0 0", color: "#555"}}>
                        Enter a learning goal and optional preferences to generate curated learning paths.
                    </p>
                </header>

                <div
                    style={{
                        background: "#fff",
                        border: "1px solid #e9e9ef",
                        borderRadius: 16,
                        padding: 16,
                        boxShadow: "0 6px 18px rgba(20, 20, 40, 0.06)",
                    }}
                >
                    <LearningForm onSubmit={handleSubmit} disabled={status === "loading"}/>

                    <div style={{marginTop: 12, color: "#555"}}>
                        {status === "idle" && (
                            <div>Tip: try “UX design online while working full-time”.</div>
                        )}

                        {status === "loading" && (
                            <div style={{display: "flex", alignItems: "center", gap: 8}}>
                                <Spinner size={16}/>
                                <div>Searching, extracting, and organizing learning paths…</div>
                            </div>
                        )}


                        {status === "error" && (
                            <div style={{color: "crimson"}}>
                                Something went wrong. {error}
                            </div>
                        )}
                    </div>
                </div>

                {data && (
                    <div style={{marginTop: 16}}>
                        <ResultsTables results={data.results}/>

                        <Warnings warnings={data.warnings}/>

                        <div style={{marginTop: 12, color: "#777", fontSize: 12}}>
                            request_id: {data.request_id}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
