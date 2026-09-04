from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.api.dependencies import get_current_user, get_faculty_user, get_placement_officer, get_current_student
from app.models.student import Student
from app.models.placement import PlacementJob
from app.models.user import User
from app.schemas.analytics import (
    StudentRiskMetrics, 
    PlacementPrediction, 
    PlacementJobCreate, 
    PlacementJobResponse,
    FacultyAnalyticsOverview,
    PlacementOfficerAnalyticsOverview
)
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

# --- Faculty Analytics Endpoints ---

@router.get("/faculty/overview", response_model=FacultyAnalyticsOverview)
def get_faculty_overview(
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    students = db.query(Student).all()
    if not students:
        return {
            "total_students": 0,
            "average_cgpa": 0.0,
            "average_attendance": 0.0,
            "risk_count": 0,
            "department": "Computer Science"
        }
    
    total = len(students)
    avg_cgpa = sum(s.current_cgpa for s in students) / total
    avg_attendance = sum(s.attendance_rate for s in students) / total
    
    risk_count = 0
    for s in students:
        risk_metrics = analytics_service.predict_student_risk(db, s)
        if risk_metrics.risk_level in ["High", "Medium"]:
            risk_count += 1
            
    return {
        "total_students": total,
        "average_cgpa": round(avg_cgpa, 2),
        "average_attendance": round(avg_attendance, 2),
        "risk_count": risk_count,
        "department": "All Departments"
    }

@router.get("/faculty/students-risk", response_model=List[StudentRiskMetrics])
def get_students_risk(
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    students = db.query(Student).all()
    risk_list = []
    for s in students:
        metrics = analytics_service.predict_student_risk(db, s)
        risk_list.append(metrics)
    return risk_list

# --- Placement Analytics Endpoints ---

@router.get("/placement/overview", response_model=PlacementOfficerAnalyticsOverview)
def get_placement_overview(
    user: User = Depends(get_placement_officer),
    db: Session = Depends(get_db)
):
    jobs_count = db.query(PlacementJob).count()
    students = db.query(Student).all()
    total_students = len(students)
    
    eligible_count = sum(1 for s in students if s.current_cgpa >= 8.0)
    
    return {
        "total_jobs": jobs_count,
        "total_placed_estimate": int(total_placed_estimate_helper(total_students)),
        "eligible_students_count": eligible_count,
        "avg_matching_score": 78.5
    }

def total_placed_estimate_helper(total: int) -> float:
    return total * 0.4

@router.post("/placement/jobs", response_model=PlacementJobResponse, status_code=status.HTTP_201_CREATED)
def create_placement_job(
    job_in: PlacementJobCreate,
    user: User = Depends(get_placement_officer),
    db: Session = Depends(get_db)
):
    db_job = PlacementJob(
        company_name=job_in.company_name,
        job_title=job_in.job_title,
        job_description=job_in.job_description,
        required_skills=job_in.required_skills,
        min_cgpa=job_in.min_cgpa,
        vacancies=job_in.vacancies,
        package_details=job_in.package_details
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("/placement/jobs", response_model=List[PlacementJobResponse])
def get_all_jobs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PlacementJob).order_by(PlacementJob.created_at.desc()).all()

@router.get("/placement/matches", response_model=List[PlacementPrediction])
def get_placement_matches(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    jobs = db.query(PlacementJob).all()
    predictions = analytics_service.calculate_job_matches(student, jobs)
    return predictions
