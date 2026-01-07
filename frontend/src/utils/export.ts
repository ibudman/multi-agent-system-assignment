import type {Program} from "../types";

function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

export function exportJson(data: unknown, filename: string) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
    });
    downloadBlob(blob, filename);
}

function csvEscape(value: string): string {
    const needsQuotes = /[",\n]/.test(value);
    const escaped = value.replace(/"/g, '""');
    return needsQuotes ? `"${escaped}"` : escaped;
}

export function exportProgramsCsv(programs: Program[], filename: string) {
    const headers = [
        "program_name",
        "provider",
        "topics_covered",
        "format",
        "duration",
        "cost",
        "prerequisites",
        "location",
        "who_this_is_for",
        "source_link",
        "citation",
    ];

    const rows = programs.map((p) => [
        p.program_name,
        p.provider,
        (p.topics_covered ?? []).join("; "),
        p.format,
        p.duration,
        p.cost,
        p.prerequisites,
        p.location,
        p.who_this_is_for,
        p.source_link,
        p.citation,
    ]);

    const csv =
        headers.join(",") +
        "\n" +
        rows.map((r) => r.map((v) => csvEscape(String(v ?? ""))).join(",")).join("\n");

    const blob = new Blob([csv], {type: "text/csv;charset=utf-8"});
    downloadBlob(blob, filename);
}
