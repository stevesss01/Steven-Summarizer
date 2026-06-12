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
        Analyze this resume.
        Return plain text only.

Do not use markdown.

Do not use ** symbols.

Do not use bullet markdown.

Use clean professional formatting.

        Provide:

        ATS Score (out of 100)

        Strengths

        Weaknesses

        Missing Skills

        Suggested Improvements

        Recruiter Verdict

        Resume:

        {text[:12000]}
        """

    elif mode == "research":

        prompt = f"""
        Analyze this research paper.
        Return plain text only.

Do not use markdown.

Do not use ** symbols.

Do not use bullet markdown.

Use clean professional formatting.

        Provide:

        Executive Summary

        Problem Statement

        Methodology

        Results

        Future Scope

        Possible Viva Questions

        Research Paper:

        {text[:12000]}
        """

    else:

        prompt = f"""
        Summarize this document.
        Return plain text only.

Do not use markdown.

Do not use ** symbols.

Do not use bullet markdown.

Use clean professional formatting.

        Provide:

        Executive Summary

        Key Insights

        Important Keywords

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