# Product Requirements Document (PRD) - Learning Path Explorer

## 1. Use Case Definition

Learning Path Explorer is a system that helps users explore and compare **real learning programs from across the web** for a given topic.  
The system organizes learning options into clear learning paths by learning horizon (short-, medium-, and long-term) and highlights tradeoffs across format, goals, cost, and — when provided — geographic relevance.

The system uses real-time web data to aggregate fragmented learning options and present them in a structured, easy-to-compare format, helping users understand tradeoffs without recommending a single “best” option.

---

## 2. What the System Does

Given a learning goal, the system:
- Discovers learning programs from the web
- Extracts structured, comparable information
- Organizes programs into short-, medium-, and long-term learning paths
- Highlights tradeoffs across format, cost, goals, and location (if applicable)
- Provides source citations for transparency

---

## 3. Product Goals

- Help users understand what learning options exist for a given topic
- Reduce research time by presenting structured comparisons
- Surface meaningful tradeoffs between different learning paths
- Ensure transparency through citations and source links

---

## 4. User Input

### Required
- Free-text learning goal

### Optional Constraints (All Optional, Single-Select)
All constraints act as soft signals that guide discovery.  
They do not enforce strict filtering.

- **Format**  
  online / in-person / hybrid
- **Goal**  
  hobby / career / skill improvement
- **Budget sensitivity**  
  free / low-cost / paid
- **City**  
  Free-text; used to prioritize location-relevant options, particularly for in-person or hybrid programs

If no constraints are provided, the system infers intent from the learning goal.

#### Example Inputs
- “I want to learn painting as a hobby, preferably in person”
- “I want to learn meditation, low commitment”
- “I want to learn UX design online while working full-time”
- “I want to learn data analytics, budget-friendly, in New York”

---

## 5. User Output

The system returns a structured comparison of learning options, grouped by learning path length.

### Learning Path Grouping
- **Short-term learning**  
  Workshops, short courses, and self-paced programs
- **Medium-term learning**  
  Certificates, structured multi-week programs, bootcamps
- **Long-term learning**  
  Degrees, apprenticeships, extended programs

Each learning path is displayed as a **separate table**, containing multiple learning options (rows).

### Table Columns (Recommended Order)

| Column | Description |
|------|-------------|
| Program name | Name of the course or program |
| Provider | Organization offering the program |
| Topics covered | High-level summary of topics |
| Format | Online / in-person / hybrid |
| Duration | Estimated time commitment |
| Cost | Estimated cost (if available) |
| Prerequisites | Required or recommended background |
| Location | City or region (if applicable) |
| Who this is for | Short explanatory summary |
| Source link | Link to the original program page |
| Citation | Source reference |

Missing information is explicitly labeled as “Not specified” rather than inferred.

---

## 6. User Interface (UI)

The UI is a simple, single-page web application focused on clarity and comparison.

### High-Level Layout (Wireframe)

~~~text
Learning Path Explorer
------------------------------------------------

What do you want to learn? *
[ I want to learn UX design                              ]

Optional preferences
Format:  Any | Online | In-person | Hybrid
Goal:    Any | Hobby | Career | Skill improvement
Budget:  Any | Free | Low-cost | Paid
City:    [ New York                                      ]

[ Show Me Learning Paths ]

------------------------------------------------
Status:
- Searching...
- Extracting...
- Organizing...

------------------------------------------------
Short-term Learning     [ Export JSON ] [ Export CSV ]
Medium-term Learning    [ Export JSON ] [ Export CSV ]
Long-term Learning      [ Export JSON ] [ Export CSV ]
~~~


### UI Principles
- All constraints are optional
- Defaults are non-restrictive (“Any”)
- Results always display all three learning paths
- Focus on readability and comparison

---

## 7. Edge Cases & Error Handling

The system should handle the following scenarios gracefully:
- No relevant learning programs found
- Partial or missing data (e.g., cost or prerequisites not listed)

In all cases, the system should prefer returning partial results with clear labeling over failing the request.

---

## 8. Non-Goals

The following are explicitly out of scope:
- Personalized recommendations based on user history
- Guarantees of completeness or exhaustive coverage
- Enrollment, payment, or account creation
- Schedule-level constraints (e.g., “evenings only”)
- Learning progress tracking or follow-up recommendations