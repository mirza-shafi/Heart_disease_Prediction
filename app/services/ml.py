def determine_risk_level(probability: float) -> str:
    if probability < 0.3:
        return "Low"
    elif probability < 0.7:
        return "Moderate"
    else:
        return "High"

def determine_confidence(probability: float) -> str:
    # High confidence if prob is near 0 or near 1
    if probability < 0.2 or probability > 0.8:
        return "High"
    elif probability < 0.4 or probability > 0.6:
        return "Medium"
    else:
        return "Low"

def get_recommendation(risk_level: str) -> str:
    if risk_level == "High":
        return "High risk detected. Please consult a cardiologist immediately."
    elif risk_level == "Moderate":
        return "Moderate risk detected. Recommend scheduling a routine check-up and maintaining a healthy lifestyle."
    else:
        return "Low risk detected. Continue maintaining a healthy lifestyle."
