import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.api.dependencies import get_staff_user, get_current_user
from app.models.document import CollegeDocument
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/documents", tags=["documents"])

# Ensure uploads directory exists relative to current file path
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("general"),
    user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF and TXT files are allowed."
        )
        
    file_path = os.path.join(UPLOAD_DIR, f"{user.id}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
        
    db_doc = CollegeDocument(
        title=file.filename,
        file_path=file_path,
        doc_type=doc_type,
        is_indexed=False,
        uploaded_by=user.id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    indexed = False
    if file_ext == ".pdf":
        indexed = rag_service.index_pdf(db_doc.id, file_path, db_doc.title)
    elif file_ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            rag_service.add_document(db_doc.id, db_doc.title, content)
            indexed = True
        except Exception as e:
            print(f"Error reading text document: {e}")
            
    if indexed:
        db_doc.is_indexed = True
        db.commit()
        db.refresh(db_doc)
        
    return db_doc

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(CollegeDocument).order_by(CollegeDocument.created_at.desc()).all()

@router.post("/{doc_id}/reindex", response_model=DocumentResponse)
def reindex_document(
    doc_id: str,
    user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    doc = db.query(CollegeDocument).filter(CollegeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    file_ext = os.path.splitext(doc.file_path)[1].lower()
    indexed = False
    
    if file_ext == ".pdf":
        indexed = rag_service.index_pdf(doc.id, doc.file_path, doc.title)
    elif file_ext == ".txt":
        try:
            with open(doc.file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            rag_service.add_document(doc.id, doc.title, content)
            indexed = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading text document: {e}")
            
    if indexed:
        doc.is_indexed = True
        db.commit()
        db.refresh(doc)
    else:
        raise HTTPException(status_code=500, detail="Failed to parse and index document text.")
        
    return doc
