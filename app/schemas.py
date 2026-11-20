
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    resume_text: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class AIChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    skills: list[str] = Field(default_factory=list)


class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(min_length=30, max_length=15000)


class JobAdviceRequest(BaseModel):
    skills: list[str] = Field(min_length=1)
    preferred_roles: list[str] = Field(default_factory=list)
    location: Optional[str] = None
