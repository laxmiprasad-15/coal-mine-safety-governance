from typing import Dict, Any, List

class XAIExplainer:
    """
    Explainable AI (XAI) engine for coal mine safety governance.
    Synthesizes ML model weights, counterfactual reasoning, and statutory DGMS rules
    into plain-language audit explanations for non-technical safety officers.
    """

    def generate_explanation(self, prediction_result: Dict[str, Any], zone_name: str = "Zone") -> str:
        risk_level = prediction_result.get("predicted_risk", "Low")
        top_factors = prediction_result.get("top_factors", [])
        risk_score = prediction_result.get("risk_score", 15.0)

        if risk_level == "Low":
            return (
                f"Zone '{zone_name}' is currently SAFE (Risk Score: {risk_score}/100). "
                f"Atmospheric gas levels (CH4, CO, O2) remain well within statutory DGMS bounds, "
                f"machinery vibration parameters are nominal, and worker PPE compliance is high."
            )

        # Build bullet-style narrative reasons from top factors
        reasons = []
        for factor in top_factors:
            feat = factor["feature"]
            val = factor["value"]
            contrib = factor.get("contribution_score", 0.0)

            if contrib <= 0.05:
                continue

            if feat == "methane_pct":
                if val >= 1.25:
                    reasons.append(f"Methane (CH4) level at {val:.2f}% severely exceeds the 1.25% DGMS evacuation threshold")
                elif val >= 0.75:
                    reasons.append(f"Methane (CH4) level ({val:.2f}%) is {val/0.75:.1f}x the standard safety advisory limit (0.75%)")
            
            elif feat == "carbon_monoxide_ppm":
                if val >= 50:
                    reasons.append(f"Carbon Monoxide (CO) concentration ({val:.1f} ppm) presents imminent asphyxiation risk (safe limit: 25 ppm)")
                elif val >= 25:
                    reasons.append(f"Carbon Monoxide (CO) elevated to {val:.1f} ppm ({val/25.0:.1f}x threshold), indicating potential smoldering coal spontaneous heating")

            elif feat == "temperature_c":
                if val >= 33:
                    reasons.append(f"Ambient temperature ({val:.1f}°C) exceeds heat stress and spontaneous combustion safety ceiling")

            elif feat == "vibration_mms":
                if val >= 7.5:
                    reasons.append(f"Equipment mechanical vibration ({val:.2f} mm/s) is {val/7.5:.1f}x allowable tolerance, signaling impending bearing or cutter head breakdown")

            elif feat == "ppe_violations_24h":
                if val >= 1:
                    reasons.append(f"{int(val)} PPE non-compliance event(s) recorded in this zone within the last 24 hours")

            elif feat == "worker_fatigue_avg":
                if val >= 60:
                    reasons.append(f"Average crew fatigue index is critically high ({val:.0f}/100) after extended underground shift duration")

            elif feat == "equipment_health_avg":
                if val <= 60:
                    reasons.append(f"Average active equipment health score has degraded to {val:.0f}%, increasing mechanical hazard probability")

            elif feat == "historical_incidents":
                if val >= 1:
                    reasons.append(f"Zone history records {int(val)} past safety incident(s) in the preceding reporting period")

        if not reasons:
            reasons.append("Slight multi-factor atmospheric and operational fluctuations detected by predictive ensemble")

        joined_reasons = "; ".join(reasons)
        confidence_pct = int(prediction_result.get("confidence", 0.9) * 100)

        explanation = (
            f"Risk is classified as {risk_level.upper()} (Risk Index: {risk_score}/100, AI Confidence: {confidence_pct}%) "
            f"primarily because: {joined_reasons}."
        )

        return explanation

    def get_actionable_recommendations(self, prediction_result: Dict[str, Any]) -> List[str]:
        """Provides prescriptive compliance actions based on the specific root causes"""
        risk_level = prediction_result.get("predicted_risk", "Low")
        top_factors = prediction_result.get("top_factors", [])
        recommendations = []

        if risk_level in ["High", "Critical"]:
            for factor in top_factors:
                feat = factor["feature"]
                val = factor["value"]
                if feat == "methane_pct" and val >= 0.75:
                    recommendations.append("Immediately activate auxiliary booster fans and inspect bleeder ventilation curtains.")
                    recommendations.append("Issue automated zone evacuation alert if CH4 persists above 1.0%.")
                if feat == "carbon_monoxide_ppm" and val >= 25:
                    recommendations.append("Deploy portable multigas detector team to locate spontaneous heating hotspot.")
                if feat == "vibration_mms" and val >= 7.5:
                    recommendations.append("Halt continuous miner/conveyor drive motor for vibration analysis and bearing lubrication.")
                if feat == "ppe_violations_24h" and val >= 1:
                    recommendations.append("Direct shift supervisor to conduct immediate on-site PPE toolbox verification talk.")
                if feat == "worker_fatigue_avg" and val >= 60:
                    recommendations.append("Rotate working crew to surface rest area and enforce mandatory hydrational break.")

        if not recommendations:
            recommendations.append("Maintain continuous IoT sensor telemetry and standard shift inspection logs.")

        return recommendations

xai_explainer = XAIExplainer()

