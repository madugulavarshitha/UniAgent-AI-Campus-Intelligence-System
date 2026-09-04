import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.api.dependencies import get_faculty_user
from app.models.user import User
from app.models.student import Student, AcademicRecord
from app.models.faculty import Faculty
from app.models.faculty_attendance import FacultyAttendance
from app.models.mark import Mark
from app.models.attendance import Attendance
from app.models.skill import Skill
from app.models.project import Project
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/faculty", tags=["faculty"])

@router.get("/attendance")
def get_faculty_attendance(
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    faculty = db.query(Faculty).filter(Faculty.user_id == user.id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty profile not found for this user."
        )
    
    logs = db.query(FacultyAttendance).filter(
        FacultyAttendance.faculty_id == faculty.id
    ).order_by(FacultyAttendance.date.desc()).all()
    
    # Calculate stats
    total_days = len(logs)
    present_days = sum(1 for log in logs if log.status == "Present")
    leave_days = sum(1 for log in logs if log.status == "On Leave")
    absent_days = sum(1 for log in logs if log.status == "Absent")
    
    attendance_rate = round((present_days / (total_days - leave_days)) * 100, 1) if (total_days - leave_days) > 0 else 100.0

    return {
        "faculty_id": faculty.id,
        "employee_id": faculty.employee_id,
        "designation": faculty.designation,
        "attendance_rate": attendance_rate,
        "total_days": total_days,
        "present_days": present_days,
        "leave_days": leave_days,
        "absent_days": absent_days,
        "logs": [
            {
                "id": log.id,
                "date": log.date.strftime("%Y-%m-%d"),
                "status": log.status,
                "check_in_time": log.check_in_time,
                "check_out_time": log.check_out_time,
                "lecture_topic": log.lecture_topic
            } for log in logs
        ]
    }

@router.post("/attendance/check-in")
def check_in_faculty(
    lecture_topic: Optional[str] = None,
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    faculty = db.query(Faculty).filter(Faculty.user_id == user.id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty profile not found for this user."
        )
    
    today = datetime.date.today()
    log = db.query(FacultyAttendance).filter(
        FacultyAttendance.faculty_id == faculty.id,
        FacultyAttendance.date == today
    ).first()
    
    now_str = datetime.datetime.now().strftime("%I:%M %p")
    
    if not log:
        log = FacultyAttendance(
            faculty_id=faculty.id,
            date=today,
            status="Present",
            check_in_time=now_str,
            lecture_topic=lecture_topic
        )
        db.add(log)
    else:
        log.status = "Present"
        if not log.check_in_time:
            log.check_in_time = now_str
        else:
            log.check_out_time = now_str
        if lecture_topic:
            log.lecture_topic = lecture_topic
            
    db.commit()
    db.refresh(log)
    
    return {
        "status": "success",
        "message": "Check-in logged successfully",
        "record": {
            "date": log.date.strftime("%Y-%m-%d"),
            "status": log.status,
            "check_in_time": log.check_in_time,
            "check_out_time": log.check_out_time,
            "lecture_topic": log.lecture_topic
        }
    }

@router.get("/students")
def get_students_list(
    search: Optional[str] = None,
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    query = db.query(Student).join(User, Student.user_id == User.id)
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (Student.registration_number.ilike(f"%{search}%"))
        )
    students = query.all()
    
    results = []
    for s in students:
        risk_metrics = analytics_service.predict_student_risk(db, s)
        results.append({
            "id": s.id,
            "registration_number": s.registration_number,
            "name": s.user.full_name if s.user else "Unknown Student",
            "email": s.user.email if s.user else "",
            "department": s.department.name if s.department else "Computer Science",
            "current_semester": s.current_semester,
            "current_cgpa": s.current_cgpa,
            "attendance_rate": s.attendance_rate,
            "risk_level": risk_metrics.risk_level,
            "warning_reason": risk_metrics.warning_reason
        })
    return results

@router.get("/students/{student_id}")
def get_student_detail(
    student_id: str,
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
        
    # Get risk diagnostics
    risk_metrics = analytics_service.predict_student_risk(db, student)
    
    # Get subjects and marks
    marks_list = db.query(Mark).filter(Mark.student_id == student.id).all()
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
            
    # Get subject-wise attendance logs
    att_logs = db.query(Attendance).filter(Attendance.student_id == student.id).all()
    subject_stats = {}
    for log in att_logs:
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
            
    attendance_summary = []
    for sub, stats in subject_stats.items():
        percentage = round((stats["attended"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        attendance_summary.append({
            "subject_code": stats["subject_code"],
            "subject_name": stats["subject_name"],
            "attended": stats["attended"],
            "total": stats["total"],
            "percentage": percentage
        })
        
    # Get skills
    skills = db.query(Skill).filter(Skill.student_id == student.id).all()
    skills_list = [s.skill_name for s in skills]
    
    # Get projects
    projects = db.query(Project).filter(Project.student_id == student.id).all()
    projects_list = [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "progress": p.progress,
            "status": p.status
        } for p in projects
    ]

    return {
        "id": student.id,
        "registration_number": student.registration_number,
        "name": student.user.full_name if student.user else "Unknown Student",
        "email": student.user.email if student.user else "",
        "department": student.department.name if student.department else "Computer Science",
        "current_semester": student.current_semester,
        "current_cgpa": student.current_cgpa,
        "attendance_rate": student.attendance_rate,
        "risk_level": risk_metrics.risk_level,
        "warning_reason": risk_metrics.warning_reason,
        "marks": list(subjects_marks.values()),
        "attendance_summary": attendance_summary,
        "skills": skills_list,
        "projects": projects_list
    }

from pydantic import BaseModel, EmailStr
from app.security.jwt import get_password_hash
import uuid

class StudentCreatePayload(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    registration_number: str
    current_semester: int
    current_cgpa: float
    attendance_rate: float
    graduation_year: int

@router.post("/students", status_code=201)
def create_student_profile(
    payload: StudentCreatePayload,
    user: User = Depends(get_faculty_user),
    db: Session = Depends(get_db)
):
    # 1. Check if email is already in use
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # 2. Check if registration number already exists
    existing_reg = db.query(Student).filter(Student.registration_number == payload.registration_number).first()
    if existing_reg:
        raise HTTPException(status_code=400, detail="Registration number already exists")

    # 3. Fetch default department
    from app.models.department import Department
    dept = db.query(Department).filter(Department.code == "CSE").first()
    dept_id = dept.id if dept else None

    # 4. Create User
    new_user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role="student",
        full_name=payload.full_name
    )
    db.add(new_user)
    db.flush()  # to get new_user.id

    # 5. Create Student Profile
    new_student = Student(
        user_id=new_user.id,
        registration_number=payload.registration_number,
        department_id=dept_id,
        current_semester=payload.current_semester,
        current_cgpa=payload.current_cgpa,
        attendance_rate=payload.attendance_rate,
        graduation_year=payload.graduation_year
    )
    db.add(new_student)
    db.flush()
    
    # 6. Seed some default attendance logs & marks for this student so they have a full profile
    from app.models.subject import Subject
    subjects = db.query(Subject).all()
    
    for sub in subjects:
        # Attendance log
        from app.models.attendance import Attendance
        for i in range(10):
            date_tick = datetime.date.today() - datetime.timedelta(days=i)
            if date_tick.weekday() < 5:
                status = "Present" if i != 3 else "Absent"
                att_log = Attendance(
                    student_id=new_student.id,
                    subject_id=sub.id,
                    date=date_tick,
                    status=status
                )
                db.add(att_log)
                
        # Marks log
        from app.models.mark import Mark
        mark_int = Mark(
            student_id=new_student.id,
            subject_id=sub.id,
            marks_obtained=24.0,
            max_marks=30.0,
            assessment_type="Internal"
        )
        mark_ext = Mark(
            student_id=new_student.id,
            subject_id=sub.id,
            marks_obtained=55.0,
            max_marks=70.0,
            assessment_type="External"
        )
        db.add_all([mark_int, mark_ext])

    db.commit()
    db.refresh(new_student)
    
    return {
        "status": "success",
        "message": "Student account and profile created successfully",
        "student": {
            "id": new_student.id,
            "name": new_user.full_name,
            "email": new_user.email,
            "registration_number": new_student.registration_number
        }
    }
