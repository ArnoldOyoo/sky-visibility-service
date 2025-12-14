from fastapi import APIRouter, Query
from datetime import date

router = APIRouter()

@router.get("/visibility")
def get_visibility(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    day: date | None = None
):
    if day is None:
        day = date.today()

    return {
        "location": {"lat": lat, "lon": lon},
        "date": day,
        "visibility_score": 0,
        "summary": "Visibility calculation not implemented yet",
        "factors": {
            "cloud_cover": None,
            "moon_phase": None,
            "darkness_hours": None
        }
    }

