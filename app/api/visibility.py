from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.visibility_logic import calculate_darkness_window
from app.services.visibility_score import calculate_visibility_score
from app.services.weather_astronomy_service import WeatherAstronomyServiceSync

router = APIRouter()

# Initialize the weather/astronomy service
weather_service = WeatherAstronomyServiceSync()

def calculate_darkness_hours(darkness_window: dict) -> float:
    """
    Calculate total darkness hours from the darkness window
    """
    try:
        start_time = datetime.strptime(darkness_window['dark_start'], "%H:%M")
        end_time = datetime.strptime(darkness_window['dark_end'], "%H:%M")
        
        # Handle overnight periods
        if end_time < start_time:
            from datetime import timedelta
            duration = (24 * 60) - (start_time.hour * 60 + start_time.minute) + (end_time.hour * 60 + end_time.minute)
            hours = duration / 60
        else:
            duration = end_time - start_time
            hours = duration.total_seconds() / 3600
        
        return round(hours, 1)
    except Exception:
        return 10.0

@router.get("/visibility")
def get_visibility(lat: float, lon: float, date: str):
    """
    Get sky visibility score and details for a specific location and date.
    
    Uses real weather and astronomy APIs for accurate data.
    
    Parameters:
    - lat: Latitude (-90 to 90)
    - lon: Longitude (-180 to 180)
    - date: Date in YYYY-MM-DD or MM/DD/YYYY format
    
    Returns:
    - location: Coordinates
    - date: Requested date
    - visibility_score: Score from 0-100
    - best_time: Optimal viewing window
    - explanation: Detailed breakdown of factors
    - details: Individual factor contributions including real moon phase
    """
    
    # Validate coordinates
    if not -90 <= lat <= 90:
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not -180 <= lon <= 180:
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    
    try:
        # Fetch real astronomy data (moon phase, illumination, etc.)
        astronomy_data = weather_service.get_astronomy_data(lat, lon, date)
        
        # Fetch real cloud cover data
        cloud_cover = weather_service.get_cloud_cover(lat, lon, date)
        
        # Calculate darkness window (using real sunset/sunrise would be better)
        darkness_window = calculate_darkness_window(date)
        
        # Calculate darkness hours
        darkness_hours = calculate_darkness_hours(darkness_window)
        
        # Get moon illumination from real API data
        moon_illumination = astronomy_data["moon_illumination"]
        
        # Calculate visibility score using real data
        score_result = calculate_visibility_score(
            cloud_cover=cloud_cover,
            moon_illumination=moon_illumination,
            darkness_hours=darkness_hours,
            light_pollution=0.5
        )
        
        return {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "date": date,
            "visibility_score": score_result["visibility_score"],
            "best_time": f"{darkness_window['dark_start']} - {darkness_window['dark_end']}",
            "explanation": score_result["explanation"],
            "details": {
                "cloud_cover_percent": cloud_cover,
                "moon_illumination_percent": int(moon_illumination * 100),
                "moon_phase": astronomy_data["moon_phase"],
                "darkness_hours": darkness_hours,
                "sunrise": astronomy_data["sunrise"],
                "sunset": astronomy_data["sunset"],
                "moonrise": astronomy_data["moonrise"],
                "moonset": astronomy_data["moonset"]
            },
            "data_source": "real_api"  # Indicates real data is being used
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculating visibility: {str(e)}"
        )