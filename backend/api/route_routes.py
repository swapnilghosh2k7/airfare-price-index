"""
Domestic Route Basket Management Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.db_models import Route
from backend.models.schemas import RouteSchema, RouteBase, RouteWeightUpdate

router = APIRouter(prefix="/routes", tags=["Route Basket"])

class RouteCreate(BaseModel):
    origin: str
    destination: str
    route_code: str
    region: str
    weight: float
    traffic_volume: int

@router.get("", response_model=List[RouteSchema])
def list_routes(db: Session = Depends(get_db)):
    """Lists all domestic basket routes with DGCA passenger traffic weights"""
    return db.query(Route).order_by(Route.weight.desc()).all()

@router.post("")
def add_route(route_data: RouteCreate, db: Session = Depends(get_db)):
    """Allows administrators to add a new domestic city-pair to the representative basket"""
    existing = db.query(Route).filter(Route.route_code == route_data.route_code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Route code already exists in basket")

    new_route = Route(
        origin=route_data.origin.upper(),
        destination=route_data.destination.upper(),
        route_code=route_data.route_code.upper(),
        region=route_data.region,
        weight=route_data.weight,
        traffic_volume=route_data.traffic_volume,
        is_active=True
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route

@router.post("/weight")
def update_route_weight(update: RouteWeightUpdate, db: Session = Depends(get_db)):
    """Updates the statistical DGCA weight for a specific route"""
    route = db.query(Route).filter(Route.route_code == update.route_code.upper()).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    route.weight = update.weight
    db.commit()
    return {"message": f"Updated weight for {route.route_code} to {route.weight}"}

@router.delete("/{route_code}")
def toggle_route_active(route_code: str, db: Session = Depends(get_db)):
    """Deactivates a route in the active basket"""
    route = db.query(Route).filter(Route.route_code == route_code.upper()).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    route.is_active = not route.is_active
    db.commit()
    return {"message": f"Route {route.route_code} active status changed to {route.is_active}"}
