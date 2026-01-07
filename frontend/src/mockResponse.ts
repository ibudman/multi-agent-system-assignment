import type {LearningPathsResponse} from "./types";

export const mockLearningPathsResponse: LearningPathsResponse = {
    request_id: "ceee21dd-7ca7-493f-93f8-79c4572c4b56",
    results: {
        short_term: [],
        medium_term: [
            {
                program_name: 'UX/UI Design Bootcamp',
                provider: 'Code Labs Academy',
                topics_covered: [
                    'User experience research technique',
                    'Competitor analysis',
                    'Prototyping',
                    'Information architecture',
                    'Agile and Lean methodologies',
                    'Figma',
                    'Colour theory & typography',
                ],
                format: 'online',
                duration: '12 weeks',
                cost: 'Not specified',
                prerequisites: 'Not specified',
                location: 'San Francisco',
                who_this_is_for:
                    'Our program is designed to get you up to speed quickly and confidently.',
                source_link:
                    'https://uiuxjobsboard.com/salary/ui-ux-designer/san-francisco',
                citation:
                    'https://uiuxjobsboard.com/salary/ui-ux-designer/san-francisco',
            },
            {
                program_name: 'UX/UI Design Bootcamp',
                provider: 'Code Labs Academy',
                topics_covered: [
                    'User experience research technique',
                    'Competitor analysis',
                    'Prototyping',
                    'Information architecture',
                    'Agile and Lean methodologies',
                    'Figma',
                    'Colour theory & typography',
                ],
                format: 'online',
                duration: '12 weeks',
                cost: 'Not specified',
                prerequisites: 'Not specified',
                location: 'San Francisco',
                who_this_is_for:
                    'Our program is designed to get you up to speed quickly and confidently.',
                source_link:
                    'https://www.reddit.com/r/UXDesign/comments/1kmrklq/freelance_ux_design_consulting_hourly_rate_for/',
                citation:
                    'https://www.reddit.com/r/UXDesign/comments/1kmrklq/freelance_ux_design_consulting_hourly_rate_for/',
            },
        ],
        long_term: [],
    },
    warnings: [
        "Extraction Specialist: Tavily extract failed for https://www.indeed.com/q-ux-designer-l-san-francisco,-ca-jobs.html (Failed to fetch url)",
        "Extraction Specialist: Tavily extract failed for https://www.ziprecruiter.com/Jobs/Hourly-Ux-Ui-Designer/-in-San-Francisco,CA (Failed to fetch url)",
        "Extraction Specialist: Tavily extract failed for https://www.indeed.com/q-ui-ux-designer-l-san-francisco-bay-area,-ca-jobs.html (Failed to fetch url)",
        "Extraction Specialist: Tavily extract failed for https://www.ziprecruiter.com/Jobs/Part-Time-Ux/-in-San-Francisco,CA (Failed to fetch url)",
        "Path Organizer: One or more buckets are empty: short_term, long_term.",
        "Path Organizer: Low number of programs after categorization (total=2)."
    ],
};
