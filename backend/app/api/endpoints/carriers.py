from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import Carrier
from backend.app.schemas.carrier import CarrierSchema

router = APIRouter()

@router.get("/carriers", response_model=List[CarrierSchema])
def get_carriers(db: Session = Depends(get_db)):
    return db.query(Carrier).all()
