import {useState} from "react";
import type {LearningPathsRequest, Prefs} from "../types";

export function LearningForm({
                                 onSubmit,
                                 disabled,
                             }: {
    onSubmit: (payload: LearningPathsRequest) => void;
    disabled?: boolean;
}) {
    const [query, setQuery] = useState("");
    const [format, setFormat] = useState("");
    const [goal, setGoal] = useState("");
    const [budget, setBudget] = useState("");
    const [city, setCity] = useState("");

    const labelStyle: React.CSSProperties = {
        display: "grid",
        gap: 6,
        fontSize: 13,
        color: "#2f2f3a",
    };

    const inputStyle: React.CSSProperties = {
        padding: "10px 12px",
        borderRadius: 12,
        border: "1px solid #d9d9e3",
        outline: "none",
        fontSize: 14,
        background: disabled ? "#fafafa" : "#fff",
    };

    const buttonDisabled = disabled || !query.trim();

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        const trimmed = query.trim();
        if (!trimmed) return;

        const prefs: Prefs = {
            format: (format || null) as Prefs["format"],
            goal: (goal || null) as Prefs["goal"],
            budget: (budget || null) as Prefs["budget"],
            city: city.trim() ? city.trim() : null,
        };

        onSubmit({query: trimmed, prefs});
    }

    return (
        <form onSubmit={handleSubmit} style={{display: "grid", gap: 12, maxWidth: 720}}>
            <label style={labelStyle}>
                What do you want to learn? <span style={{color: "crimson"}}>*</span>
                <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    rows={3}
                    disabled={disabled}
                    placeholder='e.g. "I want to learn UX design online while working full-time"'
                    style={{...inputStyle, resize: "vertical"}}
                />
            </label>

            <div style={{fontWeight: 700, marginTop: 4, color: "#111827"}}>
                Optional preferences
            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                    gap: 12,
                }}
            >
                <label style={labelStyle}>
                    Format
                    <select
                        value={format}
                        onChange={(e) => setFormat(e.target.value)}
                        disabled={disabled}
                        style={inputStyle}
                    >
                        <option value="">Any</option>
                        <option value="online">Online</option>
                        <option value="in-person">In-person</option>
                        <option value="hybrid">Hybrid</option>
                    </select>
                </label>

                <label style={labelStyle}>
                    Goal
                    <select
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        disabled={disabled}
                        style={inputStyle}
                    >
                        <option value="">Any</option>
                        <option value="hobby">Hobby</option>
                        <option value="career">Career</option>
                        <option value="skill improvement">Skill improvement</option>
                    </select>
                </label>

                <label style={labelStyle}>
                    Budget
                    <select
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        disabled={disabled}
                        style={inputStyle}
                    >
                        <option value="">Any</option>
                        <option value="free">Free</option>
                        <option value="low-cost">Low-cost</option>
                        <option value="paid">Paid</option>
                    </select>
                </label>

                <label style={labelStyle}>
                    City
                    <input
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        disabled={disabled}
                        placeholder="e.g. New York"
                        style={inputStyle}
                    />
                </label>
            </div>

            <button
                type="submit"
                disabled={buttonDisabled}
                style={{
                    padding: "10px 14px",
                    borderRadius: 12,
                    border: "1px solid #111827",
                    background: buttonDisabled ? "#f2f2f6" : "#111827",
                    color: buttonDisabled ? "#666" : "#fff",
                    cursor: buttonDisabled ? "not-allowed" : "pointer",
                    fontWeight: 700,
                    width: "fit-content",
                }}
            >
                Show Me Learning Paths
            </button>
        </form>
    );
}
