from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.event import Event
from app.schemas.event import EventSchema

router = APIRouter(prefix="/events", tags=["events"])

@router.get("", response_model=List[EventSchema])
def get_events(
    db: Session = Depends(get_db)
):
    # Retrieve all active campus events sorted by date
    events = db.query(Event).order_by(Event.date.asc()).all()
    return events
