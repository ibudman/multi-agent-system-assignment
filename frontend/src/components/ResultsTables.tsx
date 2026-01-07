import type {Program, Results} from "../types";
import {exportJson, exportProgramsCsv} from "../utils/export";

function Bucket({
                    title,
                    programs,
                    fileKey,
                }: {
    title: string;
    programs: Program[];
    fileKey: string;
}) {
    return (
        <section style={{marginTop: 22}}>
            <div style={{display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12}}>
                <h2 style={{margin: 0, fontSize: 18}}>
                    {title} ({programs.length})
                </h2>

                <div style={{display: "flex", gap: 8}}>
                    <button
                        type="button"
                        onClick={() => exportJson(programs, `${fileKey}.json`)}
                        style={{padding: "8px 10px", borderRadius: 10, border: "1px solid #999", background: "#fff"}}
                    >
                        Export JSON
                    </button>
                    <button
                        type="button"
                        onClick={() => exportProgramsCsv(programs, `${fileKey}.csv`)}
                        style={{padding: "8px 10px", borderRadius: 10, border: "1px solid #999", background: "#fff"}}
                    >
                        Export CSV
                    </button>
                </div>
            </div>

            {programs.length === 0 ? (
                <div style={{marginTop: 10, color: "#555"}}>No programs found.</div>
            ) : (
                <div style={{overflowX: "auto", marginTop: 10, border: "1px solid #eee", borderRadius: 12}}>
                    <table style={{width: "100%", borderCollapse: "collapse", minWidth: 1100}}>
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
                                        borderBottom: "1px solid #eee",
                                        background: "#fafafa",
                                        fontSize: 12,
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
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1", fontWeight: 600}}>
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
                                        Source
                                    </a>
                                </td>
                                <td style={{padding: 10, borderBottom: "1px solid #f1f1f1"}}>
                                    <a href={p.citation} target="_blank" rel="noreferrer">
                                        Citation
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
