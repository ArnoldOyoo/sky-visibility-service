def calculate_visibility(cloud_cover: float) -> int:
    score = max(0, min(100, int(100 - cloud_cover)))
    return score
