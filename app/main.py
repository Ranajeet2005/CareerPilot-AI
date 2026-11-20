
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, Base, get_db
from app import models

from app.schemas import (
    CandidateCreate,
    AIChatRequest,
    ResumeAnalysisRequest,
    JobAdviceRequest
)

from app.services import (
    parse_resume,
    load_jobs,
    match_jobs,
    semantic_search,
    career_assistant,
    evaluate_recommendations
)

from app.llm_service import (
    analyze_resume,
    career_chat,
    explain_job_matches
)


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="CareerPilot AI",
    description="AI-powered career guidance and job matching platform",
    version="2.0.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "project": "CareerPilot AI",
        "status": "running",
        "version": "2.0.0",
        "ai_provider": "Groq"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "ai_provider": "Groq"
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(error)}"
        )


# --------------------------------------------------
# RESUME PARSING
# --------------------------------------------------

@app.post("/resume/parse")
def resume_parse(request: ResumeAnalysisRequest):
    try:
        result = parse_resume(request.resume_text)

        return {
            "success": True,
            "parsed_resume": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Resume parsing failed: {str(error)}"
        )


# --------------------------------------------------
# CREATE CANDIDATE
# --------------------------------------------------

@app.post("/candidates")
def create_candidate(
    request: CandidateCreate,
    db: Session = Depends(get_db)
):
    try:
        existing_candidate = (
            db.query(models.Candidate)
            .filter(models.Candidate.email == request.email)
            .first()
        )

        if existing_candidate:
            raise HTTPException(
                status_code=409,
                detail="Candidate with this email already exists"
            )

        candidate = models.Candidate(
            name=request.name,
            email=request.email,
            resume_text=request.resume_text
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        return {
            "success": True,
            "candidate_id": candidate.id,
            "name": candidate.name,
            "email": candidate.email
        }

    except HTTPException:
        raise

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Candidate creation failed: {str(error)}"
        )


# --------------------------------------------------
# GET CANDIDATES
# --------------------------------------------------

@app.get("/candidates")
def get_candidates(db: Session = Depends(get_db)):
    try:
        candidates = db.query(models.Candidate).all()

        return [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email
            }
            for candidate in candidates
        ]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch candidates: {str(error)}"
        )


# --------------------------------------------------
# GET SAMPLE JOBS
# --------------------------------------------------

@app.get("/jobs")
def get_jobs():
    try:
        jobs = load_jobs()

        return {
            "success": True,
            "total_jobs": len(jobs),
            "jobs": jobs
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load jobs: {str(error)}"
        )


# --------------------------------------------------
# GET JOBS FROM DATABASE
# --------------------------------------------------

@app.get("/jobs/database")
def get_database_jobs(db: Session = Depends(get_db)):
    try:
        jobs = db.query(models.Job).all()

        return [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_mode": job.work_mode,
                "description": job.description,
                "required_skills": job.required_skills
            }
            for job in jobs
        ]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch database jobs: {str(error)}"
        )


# --------------------------------------------------
# JOB MATCHING
# --------------------------------------------------

@app.post("/jobs/match")
def job_matching(request: JobAdviceRequest):
    try:
        jobs = load_jobs()

        matches = match_jobs(
            jobs,
            request.skills,
            preferred_roles=request.preferred_roles or None,
            location=request.location,
            top_k=5
        )

        return {
            "success": True,
            "total_matches": len(matches),
            "matches": matches
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Job matching failed: {str(error)}"
        )


# --------------------------------------------------
# JOB SEARCH
# --------------------------------------------------


@app.get("/jobs/search")
def search_jobs(query: str):
    if not query.strip():
        return {
            "success": True,
            "total_results": 0,
            "results": []
        }

    jobs = load_jobs()
    search_term = query.strip().lower()

    results = []

    for job in jobs:
        searchable_text = " ".join([
            str(job.get("job_id", "")),
            str(job.get("title", "")),
            str(job.get("company", "")),
            str(job.get("location", "")),
            str(job.get("work_mode", "")),
            str(job.get("skills", "")),
            str(job.get("description", ""))
        ]).lower()

        if search_term in searchable_text:
            results.append(job)

    return {
        "success": True,
        "query": query,
        "total_results": len(results),
        "results": results
    }


# --------------------------------------------------
# RECOMMENDATION EVALUATION
# --------------------------------------------------

@app.get("/evaluation")
def recommendation_evaluation():
    try:
        jobs = load_jobs()

        result = evaluate_recommendations(jobs)

        return {
            "success": True,
            "evaluation": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(error)}"
        )


# --------------------------------------------------
# AI RESUME ANALYZER - GROQ
# --------------------------------------------------

@app.post("/ai/analyze-resume")
def ai_resume_analysis(request: ResumeAnalysisRequest):
    try:
        result = analyze_resume(request.resume_text)

        return {
            "success": True,
            "provider": "Groq",
            "analysis": result
        }

    except Exception as error:
        print("AI RESUME ERROR:", repr(error))

        raise HTTPException(
            status_code=502,
            detail=f"AI resume analysis failed: {str(error)}"
        )


# --------------------------------------------------
# AI CAREER CHAT - GROQ
# --------------------------------------------------

@app.post("/ai/chat")
def ai_chat(request: AIChatRequest):
    try:
        jobs = load_jobs()

        answer = career_chat(
            message=request.message,
            skills=request.skills,
            jobs=jobs
        )

        return {
            "success": True,
            "assistant": "CareerPilot AI",
            "provider": "Groq",
            "answer": answer
        }

    except Exception as error:
        print("AI CHAT ERROR:", repr(error))

        raise HTTPException(
            status_code=502,
            detail=f"AI Chat failed: {str(error)}"
        )


# --------------------------------------------------
# AI JOB ADVICE - GROQ
# --------------------------------------------------

@app.post("/ai/job-advice")
def ai_job_advice(request: JobAdviceRequest):
    try:
        jobs = load_jobs()

        matches = match_jobs(
            jobs,
            request.skills,
            preferred_roles=request.preferred_roles or None,
            location=request.location,
            top_k=5
        )

        explanation = explain_job_matches(
            skills=request.skills,
            matches=matches
        )

        return {
            "success": True,
            "provider": "Groq",
            "recommendations": matches,
            "ai_explanation": explanation
        }

    except Exception as error:
        print("AI JOB ADVICE ERROR:", repr(error))

        raise HTTPException(
            status_code=502,
            detail=f"AI Job Advice failed: {str(error)}"
        )
