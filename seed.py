import sys
import os
import datetime

# Add parent directory to path so app can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, engine, Base
from app.models.user import User
from app.models.student import Student, AcademicRecord, StudentSkill
from app.models.faculty import Faculty
from app.models.faculty_attendance import FacultyAttendance
from app.models.department import Department
from app.models.course import Course
from app.models.subject import Subject
from app.models.attendance import Attendance
from app.models.mark import Mark
from app.models.assignment import Assignment
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.project import Project
from app.models.company import Company
from app.models.job import Job
from app.models.job_requirement import JobRequirement
from app.models.event import Event
from app.models.notification import Notification
from app.models.agent_log import AgentLog
from app.models.chat_history import ChatHistory
from app.models.placement import PlacementJob
from app.security.jwt import get_password_hash

def seed_db():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("Inserting seed data for 20 tables...")
        
        # 1. Create Users
        users_to_create = [
            {"email": "admin@uniagent.edu", "password": "password123", "role": "admin", "full_name": "Admin Coordinator"},
            {"email": "faculty@uniagent.edu", "password": "password123", "role": "faculty", "full_name": "Dr. Alan Turing"},
            {"email": "placement@uniagent.edu", "password": "password123", "role": "placement_officer", "full_name": "Sarah Jenkins"},
            # Students
            {"email": "student1@uniagent.edu", "password": "password123", "role": "student", "full_name": "Ananya Sharma"},
            {"email": "student2@uniagent.edu", "password": "password123", "role": "student", "full_name": "Jane Smith"},
            {"email": "student3@uniagent.edu", "password": "password123", "role": "student", "full_name": "Bob Miller"},
            {"email": "student4@uniagent.edu", "password": "password123", "role": "student", "full_name": "Alice Cooper"}
        ]
        
        db_users = {}
        for u in users_to_create:
            user = User(
                email=u["email"],
                password_hash=get_password_hash(u["password"]),
                role=u["role"],
                full_name=u["full_name"]
            )
            db.add(user)
            db.flush()
            db_users[u["email"]] = user
            
        print("Created users successfully.")

        # 2. Departments
        cs_dept = Department(name="Computer Science and Engineering", code="CSE")
        ee_dept = Department(name="Electrical Engineering", code="EE")
        db.add_all([cs_dept, ee_dept])
        db.flush()

        # 3. Faculty details
        faculty_turing = Faculty(
            user_id=db_users["faculty@uniagent.edu"].id,
            employee_id="FAC2020001",
            department_id=cs_dept.id,
            designation="Professor & Head of Department"
        )
        db.add(faculty_turing)
        db.flush()

        # Seed Faculty Attendance
        faculty_attendance_records = []
        today = datetime.date.today()
        for i in range(15):
            date_tick = today - datetime.timedelta(days=i)
            if date_tick.weekday() < 5:  # Weekday
                status = "Present" if i != 5 else "On Leave"
                check_in = "09:00 AM" if status == "Present" else None
                check_out = "05:00 PM" if status == "Present" else None
                topic = f"Lecture {15-i}: Advanced AI Systems" if (status == "Present" and i % 3 == 0) else None
                faculty_attendance_records.append(
                    FacultyAttendance(
                        faculty_id=faculty_turing.id,
                        date=date_tick,
                        status=status,
                        check_in_time=check_in,
                        check_out_time=check_out,
                        lecture_topic=topic
                    )
                )
        db.add_all(faculty_attendance_records)

        # 4. Courses
        btech_cs = Course(name="B.Tech Computer Science and Engineering", code="CS_CORE", credits=160)
        btech_ee = Course(name="B.Tech Electrical Engineering", code="EE_CORE", credits=160)
        db.add_all([btech_cs, btech_ee])
        db.flush()

        # 5. Subjects
        sub_python = Subject(name="Programming in Python", code="CS601", course_id=btech_cs.id, department_id=cs_dept.id)
        sub_dbms = Subject(name="Database Management Systems", code="CS602", course_id=btech_cs.id, department_id=cs_dept.id)
        sub_stats = Subject(name="Mathematical Statistics", code="CS603", course_id=btech_cs.id, department_id=cs_dept.id)
        sub_ml = Subject(name="Machine Learning Foundations", code="CS604", course_id=btech_cs.id, department_id=cs_dept.id)
        db.add_all([sub_python, sub_dbms, sub_stats, sub_ml])
        db.flush()

        # 6. Students
        # Ananya: Strong CS Student, high CGPA, good skills
        student_john = Student(
            user_id=db_users["student1@uniagent.edu"].id,
            registration_number="REG2023001",
            department_id=cs_dept.id,
            current_semester=6,
            current_cgpa=8.8,
            attendance_rate=82.0,
            graduation_year=2024
        )
        
        student_jane = Student(
            user_id=db_users["student2@uniagent.edu"].id,
            registration_number="REG2023002",
            department_id=cs_dept.id,
            current_semester=6,
            current_cgpa=9.6,
            attendance_rate=97.0,
            graduation_year=2024
        )
        
        student_bob = Student(
            user_id=db_users["student3@uniagent.edu"].id,
            registration_number="REG2023003",
            department_id=cs_dept.id,
            current_semester=6,
            current_cgpa=5.8,
            attendance_rate=64.2,
            graduation_year=2024
        )
        
        student_alice = Student(
            user_id=db_users["student4@uniagent.edu"].id,
            registration_number="REG2023004",
            department_id=ee_dept.id,
            current_semester=6,
            current_cgpa=7.2,
            attendance_rate=83.0,
            graduation_year=2024
        )
        
        db.add_all([student_john, student_jane, student_bob, student_alice])
        db.flush()

        # 7. Seed Skills
        skills = [
            Skill(student_id=student_john.id, skill_name="Python", proficiency_level="Expert"),
            Skill(student_id=student_john.id, skill_name="SQL", proficiency_level="Expert"),
            Skill(student_id=student_john.id, skill_name="Excel", proficiency_level="Expert"),
            Skill(student_id=student_john.id, skill_name="Power BI", proficiency_level="Intermediate"),
            Skill(student_id=student_john.id, skill_name="Statistics", proficiency_level="Intermediate"),
            # Jane
            Skill(student_id=student_jane.id, skill_name="Python", proficiency_level="Expert"),
            Skill(student_id=student_jane.id, skill_name="Algorithms", proficiency_level="Expert"),
            # Bob
            Skill(student_id=student_bob.id, skill_name="Java", proficiency_level="Beginner"),
            # Alice
            Skill(student_id=student_alice.id, skill_name="Embedded C", proficiency_level="Intermediate")
        ]
        db.add_all(skills)

        # Legacy student_skills
        leg_skills = [
            StudentSkill(student_id=student_john.id, skill_name="Python", proficiency="Expert"),
            StudentSkill(student_id=student_john.id, skill_name="SQL", proficiency="Expert"),
            StudentSkill(student_id=student_john.id, skill_name="React", proficiency="Intermediate")
        ]
        db.add_all(leg_skills)

        # 8. Seed Certifications
        certs = [
            Certification(student_id=student_john.id, name="Google Data Analytics Professional", issuer="Coursera", issue_date=datetime.date(2025, 6, 1)),
            Certification(student_id=student_john.id, name="Advanced SQL Specialist", issuer="HackerRank", issue_date=datetime.date(2025, 12, 10))
        ]
        db.add_all(certs)

        # 9. Seed Projects
        projs = [
            Project(
                student_id=student_john.id, 
                title="AI Student Performance Prediction", 
                description="Machine Learning Capstone early identification dropouts.",
                progress=42, 
                status="In Progress"
            )
        ]
        db.add_all(projs)

        # 10. Seed Marks (Internal/External)
        # Subjects: Python, DBMS, Stats, ML
        marks = [
            # John (Ananya) marks
            Mark(student_id=student_john.id, subject_id=sub_python.id, assessment_type="Internal", marks_obtained=27.5, max_marks=30.0),
            Mark(student_id=student_john.id, subject_id=sub_python.id, assessment_type="External", marks_obtained=62.0, max_marks=70.0),
            
            Mark(student_id=student_john.id, subject_id=sub_dbms.id, assessment_type="Internal", marks_obtained=26.0, max_marks=30.0),
            Mark(student_id=student_john.id, subject_id=sub_dbms.id, assessment_type="External", marks_obtained=56.0, max_marks=70.0),
            
            Mark(student_id=student_john.id, subject_id=sub_stats.id, assessment_type="Internal", marks_obtained=19.5, max_marks=30.0),
            Mark(student_id=student_john.id, subject_id=sub_stats.id, assessment_type="External", marks_obtained=48.5, max_marks=70.0),
            
            Mark(student_id=student_john.id, subject_id=sub_ml.id, assessment_type="Internal", marks_obtained=25.0, max_marks=30.0),
            Mark(student_id=student_john.id, subject_id=sub_ml.id, assessment_type="External", marks_obtained=54.0, max_marks=70.0)
        ]
        db.add_all(marks)

        # Legacy AcademicRecord
        leg_records = [
            AcademicRecord(student_id=student_john.id, course_code="CS601", course_name="Programming in Python", credits=4, grade="A", attendance_percentage=88.0, semester=6),
            AcademicRecord(student_id=student_john.id, course_code="CS602", course_name="Database Systems", credits=3, grade="B+", attendance_percentage=82.0, semester=6),
            AcademicRecord(student_id=student_john.id, course_code="CS603", course_name="Mathematical Statistics", credits=3, grade="C", attendance_percentage=68.0, semester=6),
            AcademicRecord(student_id=student_john.id, course_code="CS604", course_name="Machine Learning Foundations", credits=4, grade="B", attendance_percentage=79.0, semester=6)
        ]
        db.add_all(leg_records)

        # 11. Seed Attendance Ticks (50 lectures per subject for John)
        # Python: 44 Present / 50 Total = 88%
        # DBMS: 41 Present / 50 Total = 82%
        # Stats: 34 Present / 50 Total = 68%
        # ML: 39 Present / 50 Total = 79%
        for i in range(50):
            # Python
            status_python = "present" if i < 44 else "absent"
            db.add(Attendance(student_id=student_john.id, subject_id=sub_python.id, date=datetime.date.today() - datetime.timedelta(days=i), status=status_python))
            
            # DBMS
            status_dbms = "present" if i < 41 else "absent"
            db.add(Attendance(student_id=student_john.id, subject_id=sub_dbms.id, date=datetime.date.today() - datetime.timedelta(days=i), status=status_dbms))
            
            # Stats
            status_stats = "present" if i < 34 else "absent"
            db.add(Attendance(student_id=student_john.id, subject_id=sub_stats.id, date=datetime.date.today() - datetime.timedelta(days=i), status=status_stats))
            
            # ML
            status_ml = "present" if i < 39 else "absent"
            db.add(Attendance(student_id=student_john.id, subject_id=sub_ml.id, date=datetime.date.today() - datetime.timedelta(days=i), status=status_ml))

        # 12. Seed Assignments
        assignments = [
            Assignment(student_id=student_john.id, subject_id=sub_python.id, title="FastAPI REST API Server", due_date=datetime.date.today() + datetime.timedelta(days=5), status="Pending", score=None),
            Assignment(student_id=student_john.id, subject_id=sub_dbms.id, title="SQL Views & Window Joins", due_date=datetime.date.today() - datetime.timedelta(days=2), status="Submitted", score=85.0),
            Assignment(student_id=student_john.id, subject_id=sub_stats.id, title="Probability Distributions Lab", due_date=datetime.date.today() - datetime.timedelta(days=6), status="Submitted", score=62.0),
            Assignment(student_id=student_john.id, subject_id=sub_ml.id, title="Logistic Dropout Classifiers", due_date=datetime.date.today() + datetime.timedelta(days=12), status="Pending", score=None)
        ]
        db.add_all(assignments)

        # 13. Seed Companies
        comp_abc = Company(name="ABC Technologies", website="https://abc-tech.com", industry="Consulting & Data Services")
        comp_tg = Company(name="TechGiant Corp", website="https://techgiant.com", industry="Software Products")
        db.add_all([comp_abc, comp_tg])
        db.flush()

        # 14. Seed Jobs
        job_da = Job(
            company_id=comp_abc.id,
            title="Data Analyst",
            description="Seeking a detail-oriented analyst to compile business reports. Must be fluent in SQL, Excel, and Power BI dashboards.",
            salary="8 LPA",
            location="Bangalore",
            vacancies=2
        )
        job_se = Job(
            company_id=comp_tg.id,
            title="Software Engineer Intern",
            description="Develop backend microservices and databases. Requires Python expertise.",
            salary="12 LPA",
            location="Hyderabad",
            vacancies=4
        )
        db.add_all([job_da, job_se])
        db.flush()

        # Legacy PlacementJob
        leg_job = PlacementJob(
            company_name="TechGiant Corp",
            job_title="Software Engineer Intern",
            job_description="Seeking a software development intern to work on enterprise backend services.",
            required_skills="Python,C++,System Design,Docker",
            min_cgpa=8.5,
            vacancies=3,
            package_details="15 LPA equivalent"
        )
        db.add(leg_job)

        # 15. Seed Job Requirements
        req_da = JobRequirement(
            job_id=job_da.id,
            min_cgpa=7.0,
            required_skills="Python,SQL,Excel,Power BI,Advanced SQL",
            required_branch="CSE"
        )
        req_se = JobRequirement(
            job_id=job_se.id,
            min_cgpa=8.0,
            required_skills="Python,SQL",
            required_branch="CSE"
        )
        db.add_all([req_da, req_se])

        # 16. Seed Events
        events = [
            Event(title="Multi-Agent AI & LLM Workshop", description="Hands-on coding session building coordination workflows using LangGraph and Gemini models.", date=datetime.datetime.utcnow() + datetime.timedelta(days=2), location="Seminar Hall A"),
            Event(title="Tech Fest Hackathon", description="Annual campus coding contest focused on educational software solutions.", date=datetime.datetime.utcnow() + datetime.timedelta(days=15), location="Information Science Center")
        ]
        db.add_all(events)

        # 17. Seed Notifications
        notifs = [
            Notification(user_id=db_users["student1@uniagent.edu"].id, title="Attendance Warning Triggered", message="Your cumulative attendance in Mathematical Statistics is currently 68%, which falls below the handbook minimum of 75%. Please clear this warning with your academic advisor."),
            Notification(user_id=db_users["student1@uniagent.edu"].id, title="New Placement Listing", message="ABC Technologies has posted a new vacancy for Data Analyst matching your academic profile.")
        ]
        db.add_all(notifs)

        db.commit()
        print("Database seeded successfully with 20 tables!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
