from typing import List, Dict


class RecommendationEngine:

    def generate(self, metrics: Dict) -> List[Dict]:

        recommendations: List[Dict] = []

        profit_factor = metrics.get("profit_factor")
        win_rate = metrics.get("win_rate")
        max_drawdown = metrics.get("max_drawdown")
        best_symbol = metrics.get("best_symbol")
        worst_day = metrics.get("worst_day")

        expectancy = metrics.get("expectancy")
        health_score = metrics.get("health_score")
        health_classification = metrics.get("health_classification")
        best_hour = metrics.get("best_hour")
        worst_hour = metrics.get("worst_hour")
        best_duration = metrics.get("best_duration_bucket")
        worst_duration = metrics.get("worst_duration_bucket")

        # -------------------------------------------------------
        # Risk / Reward structure
        # -------------------------------------------------------
        if profit_factor is not None and win_rate is not None:
            if win_rate > 65 and profit_factor < 1.2:
                recommendations.append({
                    "type": "risk_management",
                    "message": "Win rate is high but profit factor is low. Losses may be too large compared to wins."
                })

        # -------------------------------------------------------
        # Drawdown control
        # -------------------------------------------------------
        if max_drawdown is not None:

            if max_drawdown > 25:
                recommendations.append({
                    "type": "risk",
                    "message": "Max drawdown is above 25%. Consider reducing position size or tightening risk control."
                })

            elif max_drawdown > 15:
                recommendations.append({
                    "type": "risk",
                    "message": "Drawdown is approaching elevated levels. Monitor risk exposure carefully."
                })

        # -------------------------------------------------------
        # Expectancy quality
        # -------------------------------------------------------
        if expectancy is not None:

            if expectancy < 0:
                recommendations.append({
                    "type": "risk_management",
                    "message": "Expectancy is negative. The strategy may currently have no statistical edge."
                })

            elif expectancy < 0.1:
                recommendations.append({
                    "type": "performance",
                    "message": "Expectancy is positive but weak. Improving reward-to-risk could strengthen the system."
                })

        # -------------------------------------------------------
        # Account health
        # -------------------------------------------------------
        if health_classification:

            if health_classification.lower() == "critical":
                recommendations.append({
                    "type": "risk",
                    "message": "Account health is critical. Reducing risk exposure may help stabilise performance."
                })

            elif health_classification.lower() == "fragile":
                recommendations.append({
                    "type": "risk_management",
                    "message": "Account health is fragile. Consider trading smaller until stability improves."
                })

        # -------------------------------------------------------
        # Best symbol focus
        # -------------------------------------------------------
        if best_symbol:
            recommendations.append({
                "type": "performance",
                "message": f"{best_symbol} is currently your best performing symbol."
            })

        # -------------------------------------------------------
        # Weak trading day
        # -------------------------------------------------------
        if worst_day:
            recommendations.append({
                "type": "timing",
                "message": f"{worst_day} is currently your weakest trading day."
            })

        # -------------------------------------------------------
        # Time of day insight
        # -------------------------------------------------------
        if best_hour:
            recommendations.append({
                "type": "timing",
                "message": f"Trades around {best_hour}:00 show stronger performance."
            })

        if worst_hour:
            recommendations.append({
                "type": "timing",
                "message": f"Trades around {worst_hour}:00 tend to underperform."
            })

        # -------------------------------------------------------
        # Trade duration behaviour
        # -------------------------------------------------------
        if best_duration:
            recommendations.append({
                "type": "performance",
                "message": f"{best_duration} duration trades currently show the strongest performance."
            })

        if worst_duration:
            recommendations.append({
                "type": "performance",
                "message": f"{worst_duration} duration trades tend to underperform."
            })

        return recommendations