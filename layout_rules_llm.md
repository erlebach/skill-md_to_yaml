# Layout Rules for LLM Slide Generation (deduplicated from layout_rules.md)

> **Note:** Rendering details (fonts, colors, spacing) are handled by the compiler. This document covers ONLY layout selection and content structure decisions.

---

## I. Foundation Principles

### 1. One Message Per Slide Rule
- Each slide must communicate a single, clear message
- The layout choice should reinforce that message
- If you need two messages, create two slides

### 2. Visual Hierarchy Triangle
- **Primary**: The main message (largest, highest contrast)
- **Secondary**: Supporting details (medium size, medium contrast)
- **Tertiary**: Metadata/context (smallest, lowest contrast)

### 3. Cognitive Load Management
- Maximum 5-7 bullet points per content slide
- Maximum 3-4 cards/sections per two-column or comparison slide
- One complex visual (diagram/figure) per slide unless comparison is the point

---

## II. Layout-Specific Usage Rules

### title
**Purpose**: Opening slide, section breaks, major transitions

**When to Use**:
- Use at presentation start (always)
- Use for major section transitions (2-4 times in a 20-slide deck)
- Use for major section transitions after 4-6 content slides
- Do NOT use for minor topic changes (use divider instead)

---

### hero
**Purpose**: High-impact statement, key takeaway, emotional hook

**When to Use**:
- Use sparingly: 1-3 times per presentation
- Mission statement or main thesis
- Dramatic reveal of key insight
- Call to action at end
- Do NOT use for routine information delivery

---

### content
**Purpose**: Primary workhorse for text-based information

**When to Use**:
- Listing features, benefits, requirements
- Explaining processes step-by-step (use **steps** if sequential)
- Key takeaways or recommendations
- Do NOT use for dense explanations (use **two-column** with visual)

---

### two-column
**Purpose**: Pairing visual + text, showing relationships, before/after

**When to Use**:
- Explaining architecture with diagram + key points
- Process flow (Mermaid) + explanation
- Photo/screenshot + feature bullets
- Before/after comparison
- Do NOT use when visual doesn't directly support text

---

### figure
**Purpose**: Showcasing visual evidence, screenshots, photos, architecture

**When to Use**:
- Showing user interface or product
- Displaying data visualization that speaks for itself
- Presenting architecture diagram or system overview
- Photo evidence or real-world example
- Do NOT use when the visual needs significant text explanation (use **two-column**)

---

### diagram
**Purpose**: Complex technical diagrams rendered via Mermaid, network graphs, system architecture

**When to Use**:
- Network topology or system architecture
- Data flow or process diagrams
- Relationship maps (mind maps, org charts)
- Do NOT use for simple flowcharts (use **steps** or **two-column** with Mermaid)

---

### steps
**Purpose**: Sequential processes, numbered procedures, timelines

**When to Use**:
- Workflow or process (sign-up flow, algorithm steps)
- Timeline of events
- Implementation phases
- Decision tree with clear sequential logic
- Do NOT use for non-sequential lists (use **content**)
- Do NOT use when there are more than 6 steps (split into phases)

---

### comparison
**Purpose**: Side-by-side comparison, A vs B, pros/cons

**When to Use**:
- Comparing tools, approaches, methodologies
- Before/after results
- Current state vs. future state
- Do NOT use for more than 3 items (use **table**)

---

### table
**Purpose**: Structured data, feature matrices, multi-item comparison

**When to Use**:
- Feature comparison across multiple products
- Requirements matrix or specification sheet
- Schedule or agenda (time-based rows)
- Results summary with multiple dimensions
- Do NOT use for complex nested data (simplify first)
- Do NOT use for more than 10 rows (split or use appendix)

---

### code
**Purpose**: Showing code snippets, configuration, command examples

**When to Use**:
- Demonstrating API usage
- Showing configuration examples
- Teaching programming concepts
- Terminal commands or scripts
- Do NOT use for full program listings (link to repo instead)
- Do NOT use for more than one code block per slide (use **two-column** if comparing)

---

### quote
**Purpose**: Expert testimony, user feedback, memorable statements

**When to Use**:
- Expert endorsement of your approach
- User testimonial or feedback
- Defining concept with authoritative source
- Problem statement from stakeholder
- Do NOT use for your own words
- Do NOT use for generic motivational quotes

---

### summary
**Purpose**: Recap, key takeaways, conclusion slide

**When to Use**:
- End of presentation (required)
- End of major section (optional, if section >8 slides)
- Transition before Q&A
- Do NOT use at beginning of presentation (use **title** or **hero**)

---

### divider
**Purpose**: Visual break, breath, section transition (lighter than title slide)

**When to Use**:
- Brief pause between related topics
- Signaling shift in perspective or approach
- "Questions?" slide before Q&A
- Humor break or palate cleanser
- Do NOT use for major section transitions (use **title**)

---

## III. Layout Decision Tree

```
START: What is the primary purpose of this slide?

├─ Opening/Transition?
│  ├─ Major section → title
│  └─ Minor break → divider
│
├─ Making emotional impact?
│  └─ → hero
│
├─ Presenting information?
│  ├─ Pure text list? → content
│  ├─ Sequential process? → steps
│  ├─ Comparing 2-3 things? → comparison
│  ├─ Structured data grid? → table
│  └─ Text + visual needed?
│     └─ → two-column
│
├─ Showing visual evidence?
│  ├─ Simple image/screenshot → figure
│  └─ Complex diagram → diagram
│
├─ Demonstrating code/commands?
│  └─ → code
│
├─ Supporting with authority?
│  └─ → quote
│
└─ Summarizing/concluding?
   └─ → summary
```

---

## IV. Content-to-Layout Mapping Table

| Content Type | Primary Layout | Secondary Option | Avoid |
|--------------|----------------|------------------|-------|
| Features list | content | two-column (with icon/image) | table |
| Architecture | diagram | two-column (mermaid + bullets) | content |
| Process/workflow | steps | two-column (mermaid + content) | content |
| Before/after | comparison | two-column | content |
| Product demo | figure | two-column (figure + bullets) | content |
| Data results | table | figure (chart) | content |
| API example | code | two-column (code + explanation) | content |
| User feedback | quote | content (multiple quotes as bullets) | hero |
| Call to action | hero | summary | content |

---

## V. Layout Variety Rules

### The 3-Slide Rule
Never use the same layout for more than 3 consecutive slides (except during dense technical sections where consistency aids comprehension).

### The Variety Principle
In a 20-slide deck:
- **content**: 6-8 slides (most common)
- **two-column**: 3-5 slides
- **figure/diagram**: 2-4 slides
- **title**: 2-3 slides
- **Other layouts**: 1-2 each as needed

### The Transition Signal
Changing layout = signaling change in content type or importance:
- Same layout = "more of the same"
- Different layout = "pay attention, shift happening"

### The Progressive Disclosure Pattern
For complex topics, use this sequence:
1. **hero**: State the problem/question
2. **content**: List the key aspects
3. **two-column** or **diagram**: Show the solution
4. **summary**: Reinforce takeaway

---

## VI. Structure Rules

### Opening Sequence (3-4 slides)
1. **title**: Presentation title
2. **hero** or **content**: Agenda or hook
3. **content** or **figure**: Problem/context

### Body Structure (per major section)
- **title**: Section opener
- 4-8 content slides using appropriate layouts
- **summary**: Section recap (if section >8 slides)
- Optional **divider** before next section

### Closing Sequence (2-3 slides)
1. **summary**: Key takeaways
2. **hero**: Call to action or final message
3. Optional **content**: Contact/resources/next steps

### Slide Count Guidance
- Short talk (15 min): 12-18 slides
- Standard talk (30 min): 20-30 slides
- Workshop (60 min): 35-50 slides
- Each major section: 5-10 slides
- When in doubt, prefer more slides with less content per slide
