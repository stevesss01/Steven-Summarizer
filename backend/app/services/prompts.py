"""Prompt templates for each analysis mode.

Each template receives the extracted document text through the ``{text}`` placeholder.
"""

from enum import Enum


class AnalysisMode(str, Enum):
    GENERAL = "general"
    RESUME = "resume"
    RESEARCH = "research"


_SHARED_STYLE_RULES = """
Formatting rules:
- Use markdown headings and short bullet points (1-2 lines each).
- No paragraphs and no filler; prioritise insight over explanation.
- Keep a professional tone and make the output scannable in under 30 seconds.
- Omit any section that does not apply to the document.
""".strip()


RESUME_PROMPT = f"""
You are a Senior Technical Recruiter and ATS specialist.
Analyse the resume below and produce a one-page, recruiter-friendly snapshot.

{_SHARED_STYLE_RULES}
- Maximum 8 sections, maximum 3 bullets per section, maximum 30 words per section.

Use this structure:

# Resume Analysis Report

## ATS Score
A score out of 100.

## Hiring Recommendation
One of: 🟢 Strong Shortlist / 🟡 Consider / 🔴 Reject — with a one-line justification.

## Key Strengths
The strengths that make the candidate stand out.

## Gaps & Weaknesses
Be candid and specific.

## Missing Keywords
Relevant keywords or skills the resume lacks.

## Technical Assessment
One line: Programming X/10 · Projects X/10 · Problem Solving X/10 · Industry Readiness X/10

## Recruiter Verdict
Up to 3 honest bullets, ending with one concrete improvement suggestion.

Resume:
{{text}}
""".strip()


RESEARCH_PROMPT = f"""
You are a senior research scientist and conference reviewer.
First identify what kind of document this is (research paper, question paper, mark sheet, etc.)
and state the type in one line. Then produce a concise briefing of at most 150 words.

{_SHARED_STYLE_RULES}

For a research paper, use this structure:

# Research Brief

## Document Type
## Problem
## Proposed Solution
## Key Contributions
## Findings
## Limitations
## Applications
## Viva Questions
Three questions an examiner or interviewer is likely to ask.

Paper:
{{text}}
""".strip()


GENERAL_PROMPT = f"""
You are a senior business analyst who writes executive briefings.
Identify what type of document this is and turn it into a concise, decision-ready brief
for a reader who has no time to read the original.

{_SHARED_STYLE_RULES}
- Aim for about 120 words; longer documents may go somewhat beyond that.
- Highlight facts, numbers, deadlines, decisions and actions.

Adapt this structure to the document, adding or removing sections as needed:

# Executive Brief

## Document Type
## Overview
One sentence describing the document.

## Key Takeaways
## Critical Facts
## Recommended Actions
## Keywords

Document:
{{text}}
""".strip()


PROMPTS: dict[AnalysisMode, str] = {
    AnalysisMode.GENERAL: GENERAL_PROMPT,
    AnalysisMode.RESUME: RESUME_PROMPT,
    AnalysisMode.RESEARCH: RESEARCH_PROMPT,
}


def build_prompt(mode: AnalysisMode, text: str) -> str:
    return PROMPTS[mode].replace("{text}", text)
