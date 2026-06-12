import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)


def generate_summary(
    text,
    mode
):

    if mode == "resume":

        prompt = f"""
        
You are a Senior Technical Recruiter and ATS Specialist.

Analyze the resume and generate a concise, recruiter-friendly report.

IMPORTANT RULES:
Generate a one-page executive snapshot.

Rules:
- Maximum 8 sections
- Maximum 3 bullets per section
- No paragraphs
- No section longer than 30 words
- Output must fit on a single screen
- Use markdown headings
- Prioritize scanability over completeness
DO NOT write essays.
DO NOT write explanations.
DO NOT write more than 3 main bullets per section.


* Use SHORT bullet points only.
* No long paragraphs.
* Maximum 1-2 lines per bullet.
* Use professional language.
* Use markdown formatting.
* Make section headings bold.
* Focus on actionable insights.
* Avoid generic explanations.
* Output must be visually scannable within 30 seconds.

try to Return ONLY the following format as per need mainly:

# Resume Analysis Report

## ATS Score

Give a score out of 100.

## Hiring Recommendation

🟢 Strong Shortlist
🟡 Consider
🔴 Reject

Include one-line justification.

## Key Strengths(main strength which stands him out)

* Point 1
* Point 2
* Point 3
* Point 4

## Gaps & Weaknesses(be very honest)

* Point 1
* Point 2
* Point 3

## Missing Keywords

* Keyword 1
* Keyword 2
* Keyword 3

## Technical Assessment

Rate in one line:(* Programming: X/10,, Projects: X/10,Problem Solving: X/10, Industry Readiness: X/10)



## Recruiter Verdict

Maximum 3 bullet points.
be brutally honest
try to give him a improvement suggetion at the end in one line.

Resume:
{text[:12000]}

        """

    elif mode == "research":

        prompt = f"""
        You are a senior research scientist and conference reviewer.

Analyze the research paper and produce a concise research briefing.

STRICT RULES:

* No paragraphs longer than 2 lines.
* Use bullet points only.
* Maximum 150 words total.
* Prioritize insights over explanation.
* Focus on what a student, researcher, or interviewer would care about.
* Use markdown formatting.
* Make the output readable within 30 seconds.
* Use SHORT bullet points only.
* No long paragraphs.
* Maximum 1-2 lines per bullet.
* Use professional language.
* Use markdown formatting.
* Make section headings bold.
* Focus on actionable insights.
* Avoid generic explanations.

Output format as per content has:(first try to get that document is research or not , give as per type it may be a markesheet or may be previous year questions, then tell user the type and give him upto 150 words summarization pointed honest and professional marking)

# Research Brief

## Problem

• One-line description

## Proposed Solution

• One-line description

## Key Contributions

• Contribution 1
• Contribution 2
• Contribution 3

## Findings

• Finding 1
• Finding 2

## Limitations

• Limitation 1
• Limitation 2

## Applications

• Application 1
• Application 2

## Viva Questions

• Question 1
• Question 2
• Question 3

Paper:

{text[:12000]}

        """

    else:

        prompt = f"""
       

Read the document , understand which type of document is that and extract the information that would be most valuable to a decision-maker who does not have time to read the full document.
STRICT RULES: if it is of 20 page, then summary will be in 5 page is the basic law.
be open that what type of document is that and give accordingly the summarization.
* No paragraphs longer than 2 lines.
* Use bullet points only.
* Maximum 150 words total.
* Prioritize insights over explanation.
* Focus on what a student, researcher, or interviewer would care about.
* Use markdown formatting.
* Make the output readable within 30 seconds.
* Use SHORT bullet points only.
* No long paragraphs.
* Maximum 1-2 lines per bullet.
* Use professional language.
* Use markdown formatting.
* Make section headings bold.
* Focus on actionable insights.
* Avoid generic explanations.
Provide if it has otherwise give as it need to be summarized:

You are a senior business analyst and executive briefing specialist.

Your task is to transform a long document into a concise, decision-ready executive brief.

STRICT RULES:

* Maximum 120 words total for general exception if input is a 20 page or more than 2 page, then you can exceed limit but not much.
* No paragraphs only single line if needed.
* Use bullet points only.
* Focus on the most important information.
* Eliminate repetition and filler.
* Output must be readable in under 20 seconds.
* Use markdown formatting.
* Highlight facts, decisions, findings, and actions.
* Never explain obvious information.
* Never write essays.

you can modify Output format as per need , leave those which are absent , add those which need to be present: 

# Executive Brief

## Overview

• One-sentence description of the document.

## Key Takeaways

• Most important insight
• Second most important insight
• Third most important insight

## Critical Facts

• Important number, statistic, deadline, or finding
• Important fact
• Important conclusion

## Recommended Actions

• Action item 1
• Action item 2

## Keywords

• keyword1 • keyword2 • keyword3 • keyword4 • keyword5

IMPORTANT:
Keep the entire response concise enough to fit on a single screen without scrolling.

Document:
{text[:12000]}
        """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return (
        response
        .choices[0]
        .message
        .content
    )