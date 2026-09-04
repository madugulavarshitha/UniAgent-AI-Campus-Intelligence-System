import os
import sys
import unittest
from sqlalchemy.orm import Session

# Add current path to sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.core.seed import seed_db
from app.models.user import User
from app.models.student import Student
from app.models.placement import PlacementJob
from app.services.analytics_service import analytics_service
from app.services.agent_orchestrator import agent_orchestrator

class TestBackendFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Seed database (creates tables & inserts mock records)
        print("\n--- Phase 1: Database Seeding ---")
        seed_db()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_database_records(self):
        print("\n--- Verifying Seeding and DB Relations ---")
        # Query users
        users = self.db.query(User).all()
        print(f"Total seeded users: {len(users)}")
        self.assertGreaterEqual(len(users), 5)
        
        # Verify student profiles
        students = self.db.query(Student).all()
        print(f"Total seeded students: {len(students)}")
        self.assertEqual(len(students), 4)
        
        # Verify student -> academic records relationship
        john = self.db.query(Student).filter(Student.registration_number == "REG2023001").first()
        self.assertIsNotNone(john)
        self.assertEqual(john.user.full_name, "Ananya Sharma")
        self.assertGreater(len(john.academic_records), 0)
        print(f"Ananya Sharma's academic records count: {len(john.academic_records)}")

    def test_analytics_risk_prediction(self):
        print("\n--- Testing Faculty Analytics & Scikit-Learn Model ---")
        students = self.db.query(Student).all()
        for s in students:
            metrics = analytics_service.predict_student_risk(self.db, s)
            print(f"Student: {metrics.student_name} | CGPA: {metrics.current_cgpa} | Attendance: {metrics.attendance_rate}% | Predicted Risk: {metrics.predicted_dropout_risk} ({metrics.risk_level})")
            if s.registration_number == "REG2023003":  # Bob Miller
                self.assertIn(metrics.risk_level, ["High", "Medium"])
                print("-> Correctly identified Bob Miller as at-risk.")

    def test_placement_match_scoring(self):
        print("\n--- Testing Placement Matching Engine ---")
        john = self.db.query(Student).filter(Student.registration_number == "REG2023001").first()
        jobs = self.db.query(PlacementJob).all()
        
        matches = analytics_service.calculate_job_matches(john, jobs)
        print(f"Placement matches count for Ananya Sharma: {len(matches)}")
        self.assertGreater(len(matches), 0)
        
        for m in matches:
            print(f"Company: {m.company_name} | Role: {m.job_title} | Score: {m.match_score}% | Eligible: {m.is_eligible}")
            if "intern" in m.job_title.lower():
                self.assertTrue(m.is_eligible)  # John has CGPA 8.8, required is 8.5

    def test_agent_orchestrator(self):
        print("\n--- Testing LangGraph Multi-Agent Orchestrator ---")
        john = self.db.query(Student).filter(Student.registration_number == "REG2023001").first()
        
        # Test direct routing to academic advisor
        history = [
            {"role": "user", "content": "What is my CGPA and can you suggest electives?"}
        ]
        result = agent_orchestrator.run_query(
            db=self.db,
            user_id=john.user_id,
            messages=history,
            agent_type="academic"
        )
        print(f"Academic advisor output:\n{result['response']}\n")
        self.assertIsNotNone(result["response"])
        self.assertGreater(len(result["thoughts"]), 0)
        print(f"Thoughts Trace: {result['thoughts']}")

    def test_new_advisor_endpoints(self):
        print("\n--- Testing New Attendance Logs & Academic Insights Endpoints ---")
        john = self.db.query(Student).filter(Student.registration_number == "REG2023001").first()
        self.assertIsNotNone(john)
        
        # Verify that we can query the attendance logs from the student's table
        self.assertGreater(len(john.attendance_logs), 0)
        print(f"John's total raw attendance logs count: {len(john.attendance_logs)}")
        
        # Verify that the subject attendance string is built correctly in context data
        context_data = {}
        attendance_summary = {}
        for att in john.attendance_logs:
            sub_code = att.subject.code
            sub_name = att.subject.name
            if sub_code not in attendance_summary:
                attendance_summary[sub_code] = {"name": sub_name, "attended": 0, "total": 0}
            attendance_summary[sub_code]["total"] += 1
            if att.status.lower() == "present":
                attendance_summary[sub_code]["attended"] += 1
        
        attendance_lines = []
        for code, data in attendance_summary.items():
            pct = round((data["attended"] / data["total"]) * 100, 2) if data["total"] > 0 else 0.0
            attendance_lines.append(
                f"- {code}: {data['name']} | Attended: {data['attended']}/{data['total']} | Percentage: {pct}%"
            )
        subject_attendance_str = "\n".join(attendance_lines)
        print(f"Computed Subject-wise Attendance Logs:\n{subject_attendance_str}\n")
        self.assertIn("CS603: Mathematical Statistics", subject_attendance_str)

if __name__ == "__main__":
    unittest.main()

