export function Warnings({warnings}: { warnings: string[] }) {
    if (!warnings?.length) return null;

    return (
        <details style={{marginTop: 14}}>
            <summary style={{cursor: "pointer", fontWeight: 600}}>
                Warnings ({warnings.length})
            </summary>
            <ul style={{marginTop: 10, color: "#8a5a00"}}>
                {warnings.map((w, i) => (
                    <li key={i} style={{marginBottom: 6}}>
                        {w}
                    </li>
                ))}
            </ul>
        </details>
    );
}
