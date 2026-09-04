from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.api.dependencies import get_current_student
from app.models.student import Student

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/recommendations")
def get_project_recommendations(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student_skills = {s.skill_name.lower() for s in student.skills_list}
    
    # Static catalog mapping
    catalog = [
      {
        "id": "proj1",
        "title": "AI Student Dropout Risk Predictor",
        "difficulty": "Intermediate",
        "technologies": ["Python", "Scikit-Learn", "FastAPI", "React"],
        "problemStatement": "Early identification of student dropout patterns using scholastic history and demographic risk triggers.",
        "objectives": [
          "Build a Scikit-Learn logistic classification model",
          "Deploy REST APIs exposing dropout classification likelihoods",
          "Design an interactive warning table UI for faculty monitoring"
        ],
        "dataset": "Socio-academic demographic dataset (4,000 instances containing GPA, attendance, and failed courses)",
        "modules": [
          "Module 1: Data preprocessing and missing value imputation",
          "Module 2: Feature correlation matrix and Logistic Regression model training",
          "Module 3: FastAPI endpoints deployment",
          "Module 4: React student risk list warning panel"
        ],
        "expectedOutput": "A functional predictive dashboard highlighting high-risk profiles with a classification accuracy of >= 85%."
      },
      {
        "id": "proj2",
        "title": "Campus Document RAG Advisor",
        "difficulty": "Advanced",
        "technologies": ["Python", "FAISS Vector Index", "LangGraph", "Gemini API"],
        "problemStatement": "Resolving unstructured student regulation search gaps using semantic retrieval augmented generation.",
        "objectives": [
          "Parse local college manuals and PDF regulations",
          "Compile FAISS indices to perform semantic similarity matches",
          "Orchestrate a chat pipeline generating structured contextual citations"
        ],
        "dataset": "College regulations handbook PDF manuals and placement guidelines data",
        "modules": [
          "Module 1: Document loader and text splitter parser",
          "Module 2: Vector embedding creation and FAISS catalog index compilation",
          "Module 3: LLM query prompt augmentation services",
          "Module 4: Chat workspace UI"
        ],
        "expectedOutput": "Conversational assistant answering regulation queries with citation file mappings."
      },
      {
        "id": "proj3",
        "title": "Placement Compatibility Matching Engine",
        "difficulty": "Intermediate",
        "technologies": ["Python", "SQL", "Power BI", "Scikit-Learn"],
        "problemStatement": "Automating placement match diagnostic scores between student skills portfolios and vacancy requirements.",
        "objectives": [
          "Construct relational schemas tracking candidate scores and job requirements",
          "Develop matching algorithms comparing skill strings and CGPA thresholds",
          "Compile interactive Power BI reports mapping placement trends"
        ],
        "dataset": "Seeded student academic performance metrics and corporate listings datasets",
        "modules": [
          "Module 1: Relational SQL DB schema configurations",
          "Module 2: Skill matching algorithm optimization",
          "Module 3: Power BI dashboard integration"
        ],
        "expectedOutput": "Interactive report detailing candidate lists sorted by match percentage scores."
      }
    ]
    
    # Filter catalog suggestions based on student skills overlap
    recommendations = []
    if "machine learning" in student_skills or "python" in student_skills:
        recommendations.append(catalog[0])
    if "sql" in student_skills:
        recommendations.append(catalog[2])
    
    # Fallback to returning all if no match
    if not recommendations:
        recommendations = catalog
        
    return recommendations
