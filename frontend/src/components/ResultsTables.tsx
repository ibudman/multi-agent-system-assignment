import type {Program, Results} from "../types";
import {exportJson, exportProgramsCsv} from "../utils/export";

const COLUMN_WIDTHS = [
    "220px", // Program name
    "160px", // Provider
    "220px", // Topics covered
    "90px",  // Format
    "110px", // Duration
    "110px", // Cost
    "160px", // Prerequisites
    "120px", // Location
    "260px", // Who this is for
    "110px", // Source link
    "110px", // Citation
];

function Bucket({
                    title,
                    programs,
                    fileKey,
                }: {
    title: string;
    programs: Program[];
    fileKey: string;
}) {
    const empty = programs.length === 0;

    return (
        <section
            style={{
                marginTop: 16,
                background: "#fff",
                border: "1px solid #e9e9ef",
                borderRadius: 16,
                padding: 14,
                boxShadow: "0 6px 18px rgba(20, 20, 40, 0.04)",
            }}
        >
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 12,
                }}
            >
                <h2 style={{margin: 0, fontSize: 16, color: "#111827"}}>
                    {title} <span style={{color: "#6b7280", fontWeight: 600}}>({programs.length})</span>
                </h2>

                <div style={{display: "flex", gap: 8}}>
                    <button
                        type="button"
                        disabled={empty}
                        onClick={() => exportJson(programs, `${fileKey}.json`)}
                        style={{
                            padding: "8px 10px",
                            borderRadius: 12,
                            border: "1px solid #d1d5db",
                            background: "#fff",
                            opacity: empty ? 0.5 : 1,
                            cursor: empty ? "not-allowed" : "pointer",
                            fontWeight: 600,
                        }}
                    >
                        Export JSON
                    </button>

                    <button
                        type="button"
                        disabled={empty}
                        onClick={() => exportProgramsCsv(programs, `${fileKey}.csv`)}
                        style={{
                            padding: "8px 10px",
                            borderRadius: 12,
                            border: "1px solid #d1d5db",
                            background: "#fff",
                            opacity: empty ? 0.5 : 1,
                            cursor: empty ? "not-allowed" : "pointer",
                            fontWeight: 600,
                        }}
                    >
                        Export CSV
                    </button>
                </div>
            </div>

            {empty ? (
                <div style={{marginTop: 10, color: "#6b7280"}}>No programs found.</div>
            ) : (
                <div
                    style={{
                        overflowX: "auto",
                        marginTop: 10,
                        border: "1px solid #eef0f4",
                        borderRadius: 12,
                    }}
                >
                    <table style={{width: "100%", borderCollapse: "collapse", minWidth: 1500}}>
                        <colgroup>
                            {COLUMN_WIDTHS.map((w, i) => (
                                <col key={i} style={{width: w}}/>
                            ))}
                        </colgroup>

                        <thead>
                        <tr>
                            {[
                                "Program name",
                                "Provider",
                                "Topics covered",
                                "Format",
                                "Duration",
                                "Cost",
                                "Prerequisites",
                                "Location",
                                "Who this is for",
                                "Source link",
                                "Citation",
                            ].map((h) => (
                                <th
                                    key={h}
                                    style={{
                                        textAlign: "left",
                                        padding: 10,
                                        borderBottom: "1px solid #eef0f4",
                                        background: "#fafafa",
                                        fontSize: 12,
                                        color: "#374151",
                                        fontWeight: 700,
                                        whiteSpace: "nowrap",
                                    }}
                                >
                                    {h}
                                </th>
                            ))}
                        </tr>
                        </thead>

                        <tbody>
                        {programs.map((p, idx) => (
                            <tr key={`${p.program_name}-${idx}`}>
                                <td style={{
                                    padding: 10,
                                    borderBottom: "1px solid #f1f1f1",
                                    fontWeight: 700,
                                    color: "#111827"
                                }}>
                                    {p.program_name}
                                </td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.provider}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>
                                    {p.topics_covered?.length ? p.topics_covered.join(", ") : "Not specified"}
                                </td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.format}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.duration}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.cost}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.prerequisites}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.location}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>{p.who_this_is_for}</td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>
                                    <a href={p.source_link} target="_blank" rel="noreferrer">
                                        View source
                                    </a>
                                </td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>
                                    <a href={p.citation} target="_blank" rel="noreferrer">
                                        View citation
                                    </a>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            )}
        </section>
    );
}

export function ResultsTables({results}: { results: Results }) {
    return (
        <div>
            <Bucket title="Short-term learning" programs={results.short_term} fileKey="short_term"/>
            <Bucket title="Medium-term learning" programs={results.medium_term} fileKey="medium_term"/>
            <Bucket title="Long-term learning" programs={results.long_term} fileKey="long_term"/>
        </div>
    );
}
