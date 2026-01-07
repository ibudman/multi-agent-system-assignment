export type Prefs = {
    format: "online" | "in-person" | "hybrid" | null;
    goal: "hobby" | "career" | "skill improvement" | null;
    budget: "free" | "low-cost" | "paid" | null;
    city: string | null;
};

export type LearningPathsRequest = {
    query: string;
    prefs?: Prefs;
};

export type Program = {
    program_name: string;
    provider: string;
    topics_covered: string[];
    format: "online" | "in-person" | "hybrid" | "Not specified";
    duration: string;
    cost: string;
    prerequisites: string;
    location: string;
    who_this_is_for: string;
    source_link: string;
    citation: string;
};

export type Results = {
    short_term: Program[];
    medium_term: Program[];
    long_term: Program[];
};

export type LearningPathsResponse = {
    request_id: string;
    results: Results
    warnings: string[];
};
