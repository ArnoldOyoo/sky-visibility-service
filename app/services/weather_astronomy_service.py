"""
Weather and Astronomy Data Service with Redis Caching
"""

import httpx
from datetime import datetime
from typing import Dict
import os
import math
from app.services.redis_cache import cache


class WeatherAstronomyServiceSync:
    """
    Weather service with Redis caching
    """
    
    def __init__(self):
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "")
        self.base_url = "https://api.weatherapi.com/v1"
        
        # Cache TTLs (in seconds)
        self.cloud_cover_ttl = 3600  # 1 hour
        self.astronomy_ttl = 86400   # 24 hours (astronomy data changes slowly)
    
    def get_cloud_cover(self, lat: float, lon: float, date: str) -> int:
        """
        Get cloud cover with caching
        """
        # Generate cache key
        cache_key = cache._generate_key(
            "cloud_cover",
            lat=lat,
            lon=lon,
            date=date
        )
        
        # Try to get from cache first
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            print(f"✅ Cache HIT: cloud_cover for {lat},{lon} on {date}")
            return cached_value
        
        print(f"❌ Cache MISS: Fetching cloud_cover from API...")
        
        # If not in cache, fetch from API
        try:
            with httpx.Client(timeout=10.0) as client:
                url = f"{self.base_url}/forecast.json"
                params = {
                    "key": self.weather_api_key,
                    "q": f"{lat},{lon}",
                    "dt": self._format_date(date),
                    "aqi": "no"
                }
                
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                cloud_cover = 30  # Default
                
                if "forecast" in data and "forecastday" in data["forecast"]:
                    forecast_day = data["forecast"]["forecastday"][0]
                    if "hour" in forecast_day:
                        night_hours = [h for h in forecast_day["hour"] 
                                      if int(h["time"].split()[1].split(":")[0]) >= 19 
                                      or int(h["time"].split()[1].split(":")[0]) <= 5]
                        if night_hours:
                            avg_cloud = sum(h["cloud"] for h in night_hours) / len(night_hours)
                            cloud_cover = int(avg_cloud)
                
                elif "current" in data:
                    cloud_cover = data["current"].get("cloud", 30)
                
                # Store in cache
                cache.set(cache_key, cloud_cover, self.cloud_cover_ttl)
                
                return cloud_cover
                    
        except Exception as e:
            print(f"Error fetching cloud cover: {e}")
            return 30
    
    def get_astronomy_data(self, lat: float, lon: float, date: str) -> Dict:
        """
        Get astronomy data with caching
        """
        # Generate cache key
        cache_key = cache._generate_key(
            "astronomy",
            lat=lat,
            lon=lon,
            date=date
        )
        
        # Try to get from cache first
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            print(f"✅ Cache HIT: astronomy data for {lat},{lon} on {date}")
            return cached_value
        
        print(f"❌ Cache MISS: Fetching astronomy data from API...")
        
        # If not in cache, fetch from API
        try:
            with httpx.Client(timeout=10.0) as client:
                url = f"{self.base_url}/astronomy.json"
                params = {
                    "key": self.weather_api_key,
                    "q": f"{lat},{lon}",
                    "dt": self._format_date(date)
                }
                
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                result = None
                
                if "astronomy" in data and "astro" in data["astronomy"]:
                    astro = data["astronomy"]["astro"]
                    
                    result = {
                        "moon_illumination": int(astro.get("moon_illumination", 50)) / 100,
                        "moon_phase": astro.get("moon_phase", "Unknown"),
                        "sunrise": astro.get("sunrise", "06:00 AM"),
                        "sunset": astro.get("sunset", "06:00 PM"),
                        "moonrise": astro.get("moonrise", "08:00 PM"),
                        "moonset": astro.get("moonset", "08:00 AM")
                    }
                    
                    # Store in cache
                    cache.set(cache_key, result, self.astronomy_ttl)
                    return result
                    
        except Exception as e:
            print(f"Error fetching astronomy data: {e}")
        
        # Fallback data
        result = {
            "moon_illumination": self._calculate_moon_illumination_fallback(date),
            "moon_phase": "Unknown",
            "sunrise": "06:00 AM",
            "sunset": "06:00 PM",
            "moonrise": "08:00 PM",
            "moonset": "08:00 AM"
        }
        
        # Cache fallback data with shorter TTL
        cache.set(cache_key, result, 1800)  # 30 minutes
        
        return result
    
    def _format_date(self, date: str) -> str:
        """Convert date to YYYY-MM-DD format"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            try:
                date_obj = datetime.strptime(date, "%m/%d/%Y")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                return datetime.now().strftime("%Y-%m-%d")
    
    def _calculate_moon_illumination_fallback(self, date: str) -> float:
        """Fallback moon calculation if API fails"""
        try:
            date_obj = datetime.strptime(self._format_date(date), "%Y-%m-%d")
        except ValueError:
            date_obj = datetime.now()
        
        reference_new_moon = datetime(2024, 1, 11)
        lunar_cycle = 29.53
        days_since = (date_obj - reference_new_moon).days
        cycle_position = (days_since % lunar_cycle) / lunar_cycle
        
        illumination = 0.5 - 0.5 * math.cos(2 * math.pi * cycle_position)
        return illumination