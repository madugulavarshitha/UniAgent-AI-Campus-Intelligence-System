from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.dependencies import get_current_student
from app.crud.student import update_student_profile
from app.schemas.student import StudentFullResponse, StudentProfileUpdate, AcademicRecordResponse
from app.models.student import Student, AcademicRecord
from app.models.mark import Mark
from app.models.attendance import Attendance
from app.models.skill import Skill
from app.models.subject import Subject

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/profile", response_model=StudentFullResponse)
def get_profile(
    student: Student = Depends(get_current_student)
):
    return student

@router.put("/profile", response_model=StudentFullResponse)
def update_profile(
    update_data: StudentProfileUpdate,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    return update_student_profile(db, student, update_data)

@router.get("/records", response_model=list[AcademicRecordResponse])
def get_academic_records(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    records = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).all()
    return records

@router.get("/performance")
def get_student_performance(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Fetch student mark listings
    marks_list = db.query(Mark).filter(Mark.student_id == student.id).all()
    
    # Structure performance results
    subjects_marks = {}
    for mark in marks_list:
        sub_code = mark.subject.code
        sub_name = mark.subject.name
        if sub_code not in subjects_marks:
            subjects_marks[sub_code] = {
                "subject_code": sub_code,
                "subject_name": sub_name,
                "internal": 0.0,
                "external": 0.0,
                "max_internal": 30.0,
                "max_external": 70.0
            }
        
        if mark.assessment_type.lower() == 'internal':
            subjects_marks[sub_code]["internal"] = mark.marks_obtained
            subjects_marks[sub_code]["max_internal"] = mark.max_marks
        else:
            subjects_marks[sub_code]["external"] = mark.marks_obtained
            subjects_marks[sub_code]["max_external"] = mark.max_marks
            
    return {
        "cgpa": student.current_cgpa,
        "semester": student.current_semester,
        "marks": list(subjects_marks.values())
    }

@router.get("/attendance")
def get_student_attendance_summary(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Retrieve student raw attendance checks
    logs = db.query(Attendance).filter(Attendance.student_id == student.id).all()
    
    # Compile stats subject-wise
    subject_stats = {}
    for log in logs:
        sub_code = log.subject.code
        sub_name = log.subject.name
        if sub_code not in subject_stats:
            subject_stats[sub_code] = {
                "subject_code": sub_code,
                "subject_name": sub_name,
                "attended": 0,
                "total": 0
            }
        
        subject_stats[sub_code]["total"] += 1
        if log.status.lower() == 'present':
            subject_stats[sub_code]["attended"] += 1
            
    result = []
    for sub, stats in subject_stats.items():
        percentage = round((stats["attended"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        status = "Good"
        if percentage < 75:
            status = "Warning"
        elif percentage < 65:
            status = "Critical"
            
        result.append({
            "subject_code": stats["subject_code"],
            "subject_name": stats["subject_name"],
            "attended": stats["attended"],
            "total": stats["total"],
            "percentage": percentage,
            "status": status
        })
        
    return result

@router.get("/skills")
def get_student_skills_summary(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Fetch skill listings
    skills = db.query(Skill).filter(Skill.student_id == student.id).all()
    skills_data = [{"skill_name": s.skill_name, "proficiency_level": s.proficiency_level} for s in skills]
    
    # Calculate mock missing skill gaps compared to a standard Data Analyst profile
    # Target Data Analyst benchmark: Python, SQL, Excel, Power BI, Statistics, Advanced SQL, Cloud
    student_skills_set = {s.skill_name.lower() for s in skills}
    required_skills = ["python", "sql", "excel", "power bi", "statistics", "advanced sql", "cloud"]
    
    gaps = [req.title() for req in required_skills if req not in student_skills_set]
    
    return {
        "skills": skills_data,
        "gaps": gaps
    }

@router.get("/attendance/logs")
def get_student_attendance_logs(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    logs = db.query(Attendance).filter(Attendance.student_id == student.id).order_by(Attendance.date.desc()).all()
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "date": log.date.isoformat() if log.date else None,
            "subject_code": log.subject.code,
            "subject_name": log.subject.name,
            "status": log.status
        })
    return result

