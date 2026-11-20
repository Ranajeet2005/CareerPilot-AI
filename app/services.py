
import csv
import re
from pathlib import Path


# =====================================
# 1. SKILLS DATABASE
# =====================================

SKILLS_DATABASE = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "FastAPI",
    "Django",
    "Flask",
    "Spring Boot",
    "React",
    "Node.js",
    "Docker",
    "AWS",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "LLM",
    "LangChain",
    "LangGraph",
    "RAG",
    "Embeddings",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "XGBoost",
    "PyTorch",
    "TensorFlow",
    "Git",
    "Linux",
    "REST API",
    "Redis",
    "Tool Calling"
]


# =====================================
# 2. TEXT PREPROCESSING
# =====================================

def tokenize(text):

    return set(
        re.findall(
            r"[a-zA-Z][a-zA-Z+#.]*",
            text.lower()
        )
    )


# =====================================
# 3. RESUME SKILL EXTRACTION
# =====================================

def extract_skills(resume_text):

    text = resume_text.lower()

    found_skills = []

    for skill in SKILLS_DATABASE:

        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(skill.lower())
            + r"(?![a-z0-9+#])"
        )

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(set(found_skills))


# =====================================
# 4. RESUME PARSER
# =====================================

def parse_resume(resume_text):

    skills = extract_skills(resume_text)

    words = re.findall(
        r"\b\w+\b",
        resume_text
    )

    return {
        "skills": skills,
        "total_skills": len(skills),
        "word_count": len(words),
        "summary": "Resume processed successfully"
    }


# =====================================
# 5. LOAD JOBS FROM CSV
# =====================================
def load_jobs():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "jobs.csv"

    if not csv_path.exists():
        return []

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        lines = (line for line in file if line.strip())
        reader = csv.DictReader(lines)

        jobs = []

        for row in reader:
            if not row:
                continue

            job = {
                str(key).strip().lower(): str(value or "").strip()
                for key, value in row.items()
                if key is not None
            }

            if job.get("title") and job.get("company"):
                jobs.append(job)

        return jobs


# =====================================
# 6. SKILL MATCHING
# =====================================

def calculate_skill_match(
    candidate_skills,
    required_skills
):

    candidate_set = {
        skill.strip().lower()
        for skill in candidate_skills
    }

    required_set = {
        skill.strip().lower()
        for skill in required_skills
    }

    if not required_set:
        return 0, [], []

    matched = candidate_set.intersection(
        required_set
    )

    missing = required_set.difference(
        candidate_set
    )

    score = (
        len(matched) / len(required_set)
    ) * 100

    return (
        round(score, 2),
        sorted(matched),
        sorted(missing)
    )


# =====================================
# 7. JOB RECOMMENDATION ENGINE
# =====================================

def match_jobs(
    jobs,
    candidate_skills,
    preferred_roles=None,
    location=None,
    top_k=10
):

    preferred_roles = preferred_roles or []

    ranked_jobs = []

    for job in jobs:

        required_skills = (
            job.get("skills", "").split(";")
        )

        skill_score, matched, missing = (
            calculate_skill_match(
                candidate_skills,
                required_skills
            )
        )

        title = job.get("title", "").lower()

        role_score = (
            100
            if any(
                role.lower() in title
                for role in preferred_roles
            )
            else 0
        )

        location_score = (
            100
            if location
            and location.lower() in
            job.get("location", "").lower()
            else 0
        )

        final_score = (
            0.80 * skill_score
            + 0.15 * role_score
            + 0.05 * location_score
        )

        ranked_jobs.append({

            **job,

            "match_score": round(
                final_score, 2
            ),

            "matched_skills": matched,

            "missing_skills": missing,

            "explanation": (
                f"Matched {len(matched)} of "
                f"{len(required_skills)} listed skills."
            )

        })

    return sorted(
        ranked_jobs,
        key=lambda x: x["match_score"],
        reverse=True
    )[:max(1, min(top_k, 50))]


# =====================================
# 8. KEYWORD JOB SEARCH
# =====================================

def semantic_search(
    jobs,
    query,
    top_k=10
):

    query_terms = tokenize(query)

    results = []

    for job in jobs:

        job_text = " ".join([

            job.get("title", ""),

            job.get("company", ""),

            job.get("skills", "").replace(";", " "),

            job.get("description", "")

        ])

        job_terms = tokenize(job_text)

        if not query_terms:
            score = 0
        else:
            score = (
                len(query_terms.intersection(job_terms))
                / len(query_terms)
            ) * 100

        if score > 0:

            results.append({

                **job,

                "search_score": round(
                    score, 2
                )

            })

    return sorted(
        results,
        key=lambda x: x["search_score"],
        reverse=True
    )[:max(1, min(top_k, 50))]


# =====================================
# 9. CAREER ASSISTANT
# =====================================

def career_assistant(
    message,
    skills,
    jobs
):

    message_lower = message.lower()

    if any(
        word in message_lower
        for word in [
            "job",
            "jobs",
            "career",
            "opening",
            "internship"
        ]
    ):

        recommendations = match_jobs(
            jobs,
            skills,
            top_k=5
        )

        return {

            "response": (
                "Here are your recommended jobs."
            ),

            "recommendations": recommendations

        }

    if any(
        word in message_lower
        for word in [
            "skill",
            "learn",
            "improve",
            "roadmap"
        ]
    ):

        return {

            "response": (
                "Focus on Python, SQL, "
                "FastAPI, embeddings, "
                "RAG, LLM tool calling "
                "and Docker."
            ),

            "recommendations": []

        }

    return {

        "response": (
            "I can help you discover jobs "
            "and improve your technical skills."
        ),

        "recommendations": []

    }


# =====================================
# 10. RECOMMENDATION EVALUATION
# =====================================

def evaluate_recommendations(jobs):

    test_cases = [

        {
            "query": "Python FastAPI",
            "expected": ["Python", "FastAPI"]
        },

        {
            "query": "Java Spring Boot",
            "expected": ["Java", "Spring Boot"]
        },

        {
            "query": "Machine Learning XGBoost",
            "expected": ["Machine Learning", "XGBoost"]
        }

    ]

    results = []

    for test in test_cases:

        matches = semantic_search(
            jobs,
            test["query"],
            top_k=5
        )

        hit = any(
            any(
                skill.lower() in (
                    job.get("skills", "")
                    + " "
                    + job.get("description", "")
                ).lower()
                for skill in test["expected"]
            )
            for job in matches
        )

        results.append({

            "query": test["query"],

            "hit": hit

        })

    hit_rate = (
        sum(r["hit"] for r in results)
        / len(results)
    )

    return {

        "metric": "Synthetic Hit Rate @ 5",

        "score": round(hit_rate, 3),

        "tests": results

    }
