import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Load root .env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


class GroqService:

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is missing. Check your root .env file."
            )

        self.client = Groq(api_key=GROQ_API_KEY)

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CareerPilot AI, an expert career "
                            "assistant for students and fresh graduates. "
                            "Give practical, accurate and structured advice."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response.choices[0].message.content

            if not answer:
                raise RuntimeError("Groq returned an empty response.")

            return answer.strip()

        except Exception as error:
            raise RuntimeError(
                f"Groq API request failed: {error}"
            ) from error


def get_gemini_service():
    # Kept as an alias so existing imports in main.py continue working.
    return GroqService()


def analyze_resume(resume_text: str) -> str:

    prompt = f"""
Analyze this resume for software engineering and AI engineering roles.

Provide:
1. Resume summary
2. Technical skills identified
3. Strengths
4. Missing skills
5. ATS improvement suggestions
6. Recommended job roles
7. Actionable improvement plan

Do not invent qualifications or experience.

RESUME:
{resume_text}
"""

    return get_gemini_service().generate(prompt)


def career_chat(
    message: str,
    skills: list[str],
    jobs: list[dict]
) -> str:

    prompt = f"""
You are CareerPilot AI.

Help students with:
- Software engineering careers
- AI and machine learning
- Internship preparation
- Technical interviews
- Resume improvement
- Programming and DSA
- Job applications

Candidate skills:
{skills}

Available sample jobs:
{jobs[:10]}

Candidate question:
{message}

Give practical, personalized advice.
Use headings and bullet points.
Never invent candidate experience or job openings.
"""

    return get_gemini_service().generate(prompt)


def explain_job_matches(
    skills: list[str],
    matches: list[dict]
) -> str:

    prompt = f"""
You are an AI career advisor.

Candidate skills:
{skills}

Job matching results:
{matches}

Explain:
1. Strongest job matches
2. Why each job matches
3. Missing skills
4. Which job to prioritize
5. A practical learning roadmap

Do not invent job details or guarantee selection.
"""

    return get_gemini_service().generate(prompt)
