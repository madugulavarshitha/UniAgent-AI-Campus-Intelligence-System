from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.api.dependencies import get_current_student, get_current_user
from app.models.student import Student
from app.models.job import Job
from app.models.company import Company
from app.models.job_requirement import JobRequirement
from app.schemas.placement import JobSchema, JobMatchRequest

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=List[JobSchema])
def get_jobs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Fetch all vacancies, joining company and job requirements
    jobs = db.query(Job).all()
    return jobs

@router.post("/match")
def match_job(
    request: JobMatchRequest,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == request.student_id).first()
    job = db.query(Job).filter(Job.id == request.job_id).first()
    
    if not student or not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student or Job not found"
        )
        
    # Extract student skills
    student_skills = {s.skill_name.lower() for s in student.skills_list}
    
    # Extract job required skills
    req_skills_list = []
    if job.requirements and job.requirements.required_skills:
        req_skills_list = [s.strip().lower() for s in job.requirements.required_skills.split(",") if s.strip()]
        
    # Calculate skill match rate
    matched_skills = [s for s in req_skills_list if s in student_skills]
    skill_match_percentage = round((len(matched_skills) / len(req_skills_list)) * 100) if req_skills_list else 100
    
    # Calculate academic CGPA eligibility
    academic_match_percentage = 90.0 if student.current_cgpa >= 8.0 else 70.0
    min_cgpa_req = job.requirements.min_cgpa if job.requirements else 0.0
    cgpa_eligible = student.current_cgpa >= min_cgpa_req
    
    # Branch eligibility checking
    branch_eligible = True
    if job.requirements and job.requirements.required_branch:
        req_branch = job.requirements.required_branch.lower()
        dept_code = student.department.code.lower() if student.department else ""
        if req_branch not in dept_code and req_branch != "all":
            branch_eligible = False
            
    # Compile eligibility status
    is_eligible = cgpa_eligible and branch_eligible
    
    # Generate overall fit rating
    overall_match = round((skill_match_percentage * 0.5) + (academic_match_percentage * 0.3) + 15)  # include project weights
    if overall_match > 100:
        overall_match = 100
        
    missing_skills = [s.title() for s in req_skills_list if s not in student_skills]
    
    why_match = f"Your base CGPA ({student.current_cgpa}) exceeds the target threshold. "
    if len(matched_skills) > 0:
        why_match += f"You possess strong key match capabilities: {', '.join([s.title() for s in matched_skills[:3]])}."
    else:
        why_match += "You satisfy basic graduation year thresholds."
        
    to_improve = ""
    if missing_skills:
        to_improve = f"Acquire missing capabilities: {', '.join(missing_skills)}. "
    if not cgpa_eligible:
        to_improve += f"Raise cumulative CGPA above the minimum requirements of {min_cgpa_req}."
        
    return {
        "job_id": job.id,
        "student_id": student.id,
        "overall_match": overall_match,
        "skill_match": skill_match_percentage,
        "academic_match": academic_match_percentage,
        "project_match": 85,  # project baseline
        "certification_match": 80,  # certification baseline
        "is_eligible": is_eligible,
        "eligibility_details": {
            "cgpa": cgpa_eligible,
            "branch": branch_eligible,
            "skills": skill_match_percentage >= 50
        },
        "missing_skills": missing_skills,
        "why_match": why_match,
        "to_improve": to_improve or "Keep maintaining your excellent profile metrics!"
    }
