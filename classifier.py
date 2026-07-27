import numpy as np
from scipy import stats

class AnomalyClassifier:
    def __init__(self, history_store):
        self.history = history_store

    def classify_severity(self, rule_name, current_value, expected_value, context, deviation_pct=None):
        if deviation_pct is None:
             deviation_pct = abs(current_value - expected_value) / expected_value * 100

        # Get historical deviations for this rule
        historical = self.history.get_deviations(rule_name, days=90)

        if len(historical) > 10:
            z_score = (deviation_pct - np.mean(historical)) / np.std(historical)
        else:
            z_score = deviation_pct / 5  # Simple fallback

        # Check contextual factors
        is_holiday = context.get("is_holiday", False)
        is_month_start = context.get("day_of_month", 15) <= 2
        is_weekend = context.get("is_weekend", False)

        # Severity classification
        if deviation_pct > 10 and z_score > 3:
            severity = "CRITICAL"
        elif deviation_pct > 5 or z_score > 2.5:
            if is_holiday or is_month_start:
                severity = "WARNING"  # Downgrade if context explains it
            else:
                severity = "HIGH"
        elif deviation_pct > 2 or z_score > 2:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Record this deviation for future statistical baseline
        self.history.add_deviation(rule_name, deviation_pct)

        return {
            "severity": severity,
            "deviation_pct": round(deviation_pct, 2),
            "z_score": round(z_score, 2),
            "contextual_factors": {
                "holiday": is_holiday,
                "month_start": is_month_start,
                "weekend": is_weekend
            },
            "recommendation": self._get_recommendation(severity, rule_name)
        }

    def _get_recommendation(self, severity, rule_name):
        recommendations = {
            "CRITICAL": f"Immediate investigation required for '{rule_name}'. "
                       f"Check data source connectivity and recent pipeline runs.",
            "HIGH": f"Review '{rule_name}' within 2 hours. "
                   f"Likely data quality issue requiring attention.",
            "MEDIUM": f"Monitor '{rule_name}' over next refresh cycle. "
                     f"May self-resolve.",
            "LOW": f"Logged for trend tracking. No action needed."
        }
        return recommendations.get(severity, "Review when available.")
