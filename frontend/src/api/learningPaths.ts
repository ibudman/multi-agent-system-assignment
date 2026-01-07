import type {LearningPathsRequest, LearningPathsResponse} from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export async function fetchLearningPaths(
    payload: LearningPathsRequest,
    signal?: AbortSignal
): Promise<LearningPathsResponse> {
    const res = await fetch(`${BASE_URL}/api/learning-paths`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload),
        signal,
    });

    if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`Backend error ${res.status}: ${text || res.statusText}`);
    }

    return (await res.json()) as LearningPathsResponse;
}
