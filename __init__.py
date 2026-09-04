from app.database.connection import Base
from app.models.user import User
from app.models.student import Student, AcademicRecord, StudentSkill
from app.models.faculty import Faculty
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
from app.models.agent_history import AgentConversation, AgentMessage
from app.models.document import CollegeDocument
from app.models.placement import PlacementJob

__all__ = [
    "Base",
    "User",
    "Student",
    "AcademicRecord",
    "StudentSkill",
    "Faculty",
    "Department",
    "Course",
    "Subject",
    "Attendance",
    "Mark",
    "Assignment",
    "Skill",
    "Certification",
    "Project",
    "Company",
    "Job",
    "JobRequirement",
    "Event",
    "Notification",
    "AgentLog",
    "ChatHistory",
    "AgentConversation",
    "AgentMessage",
    "CollegeDocument",
    "PlacementJob"
]
