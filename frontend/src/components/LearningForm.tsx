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
        <form onSubmit={handleSubmit} style={{display: "grid", gap: 12, maxWidth: 700}}>
            <label style={{display: "grid", gap: 6}}>
                What do you want to learn? *
                <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    rows={3}
                    disabled={disabled}
                    placeholder='e.g. "I want to learn UX design online while working full-time"'
                />
            </label>

            <div style={{fontWeight: 600, marginTop: 6}}>Optional preferences</div>

            <div style={{display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12}}>
                <label style={{display: "grid", gap: 6}}>
                    Format
                    <select value={format} onChange={(e) => setFormat(e.target.value)} disabled={disabled}>
                        <option value="">Any</option>
                        <option value="online">Online</option>
                        <option value="in-person">In-person</option>
                        <option value="hybrid">Hybrid</option>
                    </select>
                </label>

                <label style={{display: "grid", gap: 6}}>
                    Goal
                    <select value={goal} onChange={(e) => setGoal(e.target.value)} disabled={disabled}>
                        <option value="">Any</option>
                        <option value="hobby">Hobby</option>
                        <option value="career">Career</option>
                        <option value="skill improvement">Skill improvement</option>
                    </select>
                </label>

                <label style={{display: "grid", gap: 6}}>
                    Budget
                    <select value={budget} onChange={(e) => setBudget(e.target.value)} disabled={disabled}>
                        <option value="">Any</option>
                        <option value="free">Free</option>
                        <option value="low-cost">Low-cost</option>
                        <option value="paid">Paid</option>
                    </select>
                </label>

                <label style={{display: "grid", gap: 6}}>
                    City
                    <input
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        disabled={disabled}
                        placeholder="e.g. New York"
                    />
                </label>
            </div>

            <button type="submit" disabled={disabled || !query.trim()}>
                Show Me Learning Paths
            </button>
        </form>
    );
}
