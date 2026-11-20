from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Table,
    DateTime
)
from sqlalchemy.orm import relationship

from app.database import Base


# ----------------------------------
# CANDIDATE-SKILL ASSOCIATION TABLE
# ----------------------------------

candidate_skills = Table(
    "candidate_skills",
    Base.metadata,

    Column(
        "candidate_id",
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "skill_id",
        Integer,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True
    )
)


# ----------------------------------
# CANDIDATE MODEL
# ----------------------------------

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    resume_text = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    skills = relationship(
        "Skill",
        secondary=candidate_skills,
        back_populates="candidates"
    )


# ----------------------------------
# SKILL MODEL
# ----------------------------------

class Skill(Base):
    __tablename__ = "skills"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    candidates = relationship(
        "Candidate",
        secondary=candidate_skills,
        back_populates="skills"
    )


# ----------------------------------
# JOB MODEL
# ----------------------------------

class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    company = Column(
        String(150),
        nullable=False
    )

    location = Column(
        String(150)
    )

    work_mode = Column(
        String(50)
    )

    description = Column(Text)

    required_skills = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
