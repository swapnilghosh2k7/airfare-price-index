from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import Route
from backend.app.schemas.route import RouteSchema

router = APIRouter()

@router.get("/routes", response_model=List[RouteSchema])
def get_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()
