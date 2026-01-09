export function Spinner({size = 16}: { size?: number }) {
    return (
        <span
            aria-label="Loading"
            style={{
                width: size,
                height: size,
                display: "inline-block",
                borderRadius: "50%",
                border: "2px solid rgba(0,0,0,0.15)",
                borderTopColor: "rgba(0,0,0,0.6)",
                animation: "spin 0.8s linear infinite",
            }}
        >
      <style>
        {`@keyframes spin { to { transform: rotate(360deg); } }`}
      </style>
    </span>
    );
}
