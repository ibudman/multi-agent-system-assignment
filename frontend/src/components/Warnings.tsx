export function Warnings({warnings}: { warnings: string[] }) {
    if (!warnings?.length) return null;

    return (
        <details style={{marginTop: 14}}>
            <summary style={{cursor: "pointer", fontWeight: 600}}>
                Processing notes ({warnings.length})
            </summary>

            <div style={{marginTop: 8, fontSize: 13, color: "#6b7280"}}>
                Some sources couldn’t be fetched or processed. Results may be incomplete.
            </div>

            <ul style={{marginTop: 8, color: "#8a5a00"}}>
                {warnings.map((w, i) => (
                    <li key={i} style={{marginBottom: 6}}>
                        {w}
                    </li>
                ))}
            </ul>
        </details>
    );
}
