from fastapi import APIRouter
from app.services.weather import get_cloud_cover

router = APIRouter()

@router.get("/")
def get_visibility(lat: float, lon: float):
    cloud_cover = get_cloud_cover(lat, lon)

    return {
        "lat": lat,
        "lon": lon,
        "cloud_cover": cloud_cover,
        "visibility_score": 100 - cloud_cover
    }
