def calculate_visibility_score(
    cloud_cover: float,
    moon_illumination: float,
    darkness_hours: float,
    light_pollution: float
) -> dict:
    """
    Calculate sky visibility score (0–100) based on key factors.
    """

    cloud_score = max(0, 100 - cloud_cover)
    moon_score = max(0, 100 - moon_illumination)
    darkness_score = min(100, darkness_hours * 12.5)
    pollution_score = max(0, 100 - light_pollution)

    final_score = (
        0.4 * cloud_score +
        0.3 * moon_score +
        0.2 * darkness_score +
        0.1 * pollution_score
    )

    explanation = []

    if cloud_cover > 60:
        explanation.append("Heavy cloud cover reduces visibility.")
    else:
        explanation.append("Low cloud cover is favorable.")

    if moon_illumination > 70:
        explanation.append("Bright moonlight limits faint object visibility.")
    else:
        explanation.append("Moonlight impact is minimal.")

    if darkness_hours < 4:
        explanation.append("Short dark window available.")
    else:
        explanation.append("Good duration of darkness.")

    return {
        "visibility_score": round(final_score),
        "explanation": " ".join(explanation)
    }
