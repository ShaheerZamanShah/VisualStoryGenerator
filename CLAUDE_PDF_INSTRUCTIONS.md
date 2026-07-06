# Instructions for Claude AI: Converting Project Report to PDF

Dear Claude,

Please use the attached `PROJECT_REPORT.md` file to generate a professional **8-12 page PDF report** for an Agentic AI university project. Below are the specifications and guidelines:

## PDF Specifications

### **Document Formatting**

- **Page Format:** A4 (210 × 297 mm)
- **Margins:** 1 inch (2.54 cm) on all sides
- **Font Family:** Calibri or Times New Roman
- **Body Font Size:** 11 pt
- **Heading Font Size:** 14 pt (H1), 12 pt (H2), 11 pt (H3)
- **Line Spacing:** 1.5
- **Page Numbers:** Bottom right, starting from page 1
- **Header/Footer:** Course name "Agentic AI (8th Semester)" on each page

### **Document Structure**

#### **Cover Page**

- Title: "Agentic AI Video Pipeline - Complete Project Report"
- Subtitle: "End-to-End Visual Novel Video Generator with LangGraph-Based Multi-Agent Orchestration"
- Student Information: [To be filled by submitter]
- Course: Agentic AI (8th Semester)
- Date: May 6, 2026
- Institution: [To be filled by submitter]
- Centered, professional layout with 1.5" spacing between elements

#### **Table of Contents**

- Auto-generated from document headings
- Include all main sections (1-11)
- Page numbers for each section

#### **Main Content**

- **Executive Summary:** 1 page
  - Overview of project scope and achievements
  - Key metrics highlighted
- **System Architecture:** 1.5 pages
  - Architecture diagrams (as ASCII/text, keep readable)
  - Component descriptions
  - Data flow illustration
- **Phase-Wise Implementation:** 2.5 pages
  - Story Generation (0.5 page)
  - Audio Generation (0.5 page)
  - Video Composition (1 page)
  - Edit Agent (0.5 page)
- **Tools and APIs:** 0.75 page
  - API table
  - Technology stack summary
- **JSON Schema Design:** 1 page
  - Core data models with examples
  - Validation rules
- **Challenges & Solutions:** 1.5 pages
  - 5-7 major technical challenges
  - Solutions and results
- **Results & Achievements:** 1 page
  - Functional results
  - Technical metrics
  - Performance statistics
- **Individual Contributions:** 0.75 page
  - Team member roles
  - [IMPORTANT: Blank fields for contributors to fill in names/details]
- **Lessons Learned & Future Work:** 0.5 page

### **Visual Elements**

#### **Diagrams & Tables**

- **Architecture Diagram:** Include ASCII representation or convert to simple boxes/arrows
- **Phase Flow Diagram:** Sequential Story → Audio → Video → Edit flow
- **Data Model Tables:** Format all JSON examples as tables where appropriate
- **Performance Tables:** Use professional table styling
- **Statistics Table:** Code metrics and testing summary

#### **Code Examples**

- Wrap in code blocks with light gray background (#F5F5F5)
- Use monospace font (Courier New, 9pt)
- Include syntax highlighting if possible (Python highlighting for .py snippets)
- Limit to critical code snippets (max 8-10 lines per example)

#### **Formatting Details**

- **Bold:** Project names, key terms on first mention
- **Italics:** File paths, variable names
- **Code blocks:** Backticks for inline code
- **Lists:** Bullet points with consistent indentation
- **Quotes:** Indented block quotes for important statements

### **Content Customization Areas**

The report contains **placeholder sections** that the student should fill in:

1. **Section 7 - Individual Contributions:**
   - [ ] Team Member 1: Name, Role, Responsibilities checklist, Hours
   - [ ] Team Member 2: Name, Role, Responsibilities checklist, Hours
   - [ ] Team Member 3: Name, Role, Responsibilities checklist, Hours
   - [ ] Team Member 4 (Optional): Name, Role, etc.
   - Fill in actual commit counts, hours worked, specific achievements
   - Remove unused team member sections

2. **Cover Page Data:**
   - Insert actual student names
   - Insert institution name
   - Insert course code/professor name (if available)

3. **Report Generated Date:**
   - Update to actual submission date
   - Keep format: "Month Day, Year"

## Style Guidelines for Claude

### **Professional Tone**

- Formal academic writing
- Third-person perspective (except in individual contributions)
- Active voice preferred
- Technical precision with accessibility

### **Structure**

- Each section should be self-contained
- Cross-references within document (e.g., "See Section 4.2 for schema details")
- Consistent terminology throughout

### **Terminology Consistency**

- "Edit Agent" (not "edit-agent" or "EditAgent" in prose)
- "Pollinations.ai" (exact capitalization)
- "Groq LLM" (exact capitalization)
- "WebSocket" (exact capitalization)
- "LangGraph" (exact capitalization)

### **Mathematical Notation**

- If using equations, format as LaTeX: $equation$ for inline, $$equation$$ for block
- Example: Keep the CRF quality formula and timing calculations in clear format

### **Citations & References**

- No external citations needed (internal project documentation)
- Reference internal sections: "as discussed in Section X.Y"
- Reference figures/tables: "Table 3.1 shows performance metrics"

## PDF Quality Checklist

Before finalizing, ensure:

- [ ] All pages are properly formatted with consistent margins
- [ ] Headers/footers appear on every page
- [ ] Page numbers are sequential
- [ ] Table of Contents page numbers match actual sections
- [ ] No widowed/orphaned lines (single line at top/bottom of page)
- [ ] Code blocks don't break awkwardly across pages
- [ ] All diagrams are legible and properly labeled
- [ ] Hyperlinks work (TOC links to sections)
- [ ] No spelling/grammar errors (use spell checker)
- [ ] Consistent date format throughout
- [ ] Professional cover page with proper spacing

## Export Settings

**Recommended PDF Generation Method:**

1. Generate as properly formatted document (Word, LaTeX, or Google Docs)
2. Export to PDF with these settings:
   - Compression: Balanced (for file size <5 MB)
   - Quality: 300 DPI (for clear text and images)
   - Include bookmarks from TOC
   - Include hyperlinks
   - Embed all fonts

**File Size Target:** 2-4 MB (compressed PDF with high quality)

## Special Instructions

1. **Architecture Diagram:** The ASCII art diagram in the report is intentionally designed to be PDF-friendly. Keep it as-is or convert to simple black-line boxes if ASCII doesn't render well.

2. **JSON Examples:** Format as code blocks or simple tables - whichever looks cleaner in the final PDF.

3. **Performance Data:** Ensure all numbers/statistics are clearly highlighted in boxes or tables for easy scanning.

4. **Placeholder Warnings:** Where team member names/details are blank, either:
   - Leave as "[Name]" for students to fill in later, OR
   - Generate placeholder content showing what should go there (e.g., "[Team Member 1 Name]", "[XX total commits]")

## Expected Document Length

- **Page Count:** 8-12 pages (should fit exactly with these specifications)
- **Word Count:** 4,500-6,000 words
- **Sections:** 11 main sections + appendix
- **Code Examples:** 6-8 snippets
- **Tables:** 8-10 professional tables
- **Diagrams:** 2-3 ASCII/text diagrams

---

## Quality Assurance

After generating the PDF, please verify:

1. ✅ **Content Completeness**: All 11 sections included
2. ✅ **Formatting**: Consistent fonts, margins, spacing
3. ✅ **Readability**: 11pt body font, 1.5 line spacing
4. ✅ **Professional Look**: Cover page, TOC, page numbers
5. ✅ **Technical Accuracy**: Code blocks, schemas, statistics
6. ✅ **Length**: 8-12 pages (typically 10 pages with current content)

---

## Notes for PDF Generation

- This Markdown file is structured to be PDF-friendly
- All sections are modular and can be rearranged if needed
- ASCII diagrams will render as code blocks in PDF
- Tables use Markdown syntax compatible with most PDF generators
- No external images required (all content is text/ASCII)

---

**Document prepared for:** Claude AI (ChatGPT-4 or later)  
**Purpose:** University project report PDF generation  
**Difficulty Level:** Medium complexity (multi-section, tables, custom formatting)  
**Estimated PDF generation time:** 5-10 minutes

---

**Thank you for generating this report!**
