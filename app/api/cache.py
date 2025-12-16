"""
Cache Management API Endpoints
"""

from fastapi import APIRouter, HTTPException
from app.services.redis_cache import cache

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats")
def get_cache_stats():
    """
    Get cache statistics
    
    Returns:
    - Cache status and performance metrics
    """
    stats = cache.get_stats()
    return {
        "cache_stats": stats,
        "ttl_config": {
            "cloud_cover": "1 hour",
            "astronomy": "24 hours"
        }
    }


@router.post("/clear")
def clear_cache(pattern: str = "*"):
    """
    Clear cache entries matching a pattern
    
    Parameters:
    - pattern: Redis key pattern (default: "*" clears all)
    
    Examples:
    - "*" - Clear all cache
    - "cloud_cover:*" - Clear only cloud cover cache
    - "astronomy:*" - Clear only astronomy cache
    """
    if not cache.enabled:
        raise HTTPException(
            status_code=503,
            detail="Cache is not enabled"
        )
    
    try:
        deleted = cache.clear_pattern(pattern)
        return {
            "success": True,
            "deleted_keys": deleted,
            "pattern": pattern
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.delete("/key/{key}")
def delete_cache_key(key: str):
    """
    Delete a specific cache key
    
    Parameters:
    - key: The exact cache key to delete
    """
    if not cache.enabled:
        raise HTTPException(
            status_code=503,
            detail="Cache is not enabled"
        )
    
    success = cache.delete(key)
    
    if success:
        return {
            "success": True,
            "message": f"Key '{key}' deleted"
        }
    else:
        return {
            "success": False,
            "message": f"Key '{key}' not found or error occurred"
        }


@router.get("/health")
def cache_health():
    """
    Check if cache is healthy and accessible
    """
    return {
        "enabled": cache.enabled,
        "status": "healthy" if cache.enabled else "disabled"
    }