"""
PHASE 8: Insights Generator Module (The Insights Layer)
Generate plain-English summaries explaining model predictions
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """
    Generate human-readable insights and explanations
    - Plain-English prediction summaries
    - Business-actionable insights
    - Anomaly descriptions
    - Trend identification
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.insights = []
        logger.info("InsightsGenerator initialized")
    
    def generate_prediction_insight(self, prediction: float, 
                                   feature_values: Dict[str, float],
                                   feature_contributions: Dict[str, float],
                                   target_name: str = "target",
                                   context: Dict = None) -> str:
        """
        Generate human-readable prediction explanation
        """
        logger.info(f"Generating insight for prediction: {prediction:.4f}")
        
        context = context or {}
        
        # Build narrative
        narrative = f"The model predicts {target_name} of {prediction:.2f}. "
        
        # Identify top contributing features
        sorted_contributions = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        if sorted_contributions:
            narrative += "Key drivers: "
            drivers = []
            
            for feature, contribution in sorted_contributions[:3]:
                direction = "increased" if contribution > 0 else "decreased"
                value = feature_values.get(feature, "unknown")
                drivers.append(
                    f"{feature} ({value:.2f}) {direction} the prediction by {abs(contribution):.4f}"
                )
            
            narrative += "; ".join(drivers) + ". "
        
        # Add business context if provided
        if context:
            narrative += f"This prediction was made based on {list(feature_values.keys())[0]} "
            narrative += f"and {len(feature_values)} other factors. "
        
        # Add confidence statement
        narrative += "This is a data-driven estimate based on historical patterns."
        
        return narrative
    
    def generate_batch_insights(self, predictions_df: pd.DataFrame,
                               feature_names: List[str],
                               predictions_col: str = 'predictions') -> List[Dict]:
        """
        Generate insights for a batch of predictions
        """
        logger.info(f"Generating insights for {len(predictions_df)} predictions")
        
        insights_list = []
        
        for idx, row in predictions_df.iterrows():
            prediction = row[predictions_col]
            
            feature_vals = {feat: row.get(feat, 0) for feat in feature_names}
            
            insight = {
                'index': idx,
                'prediction': float(prediction),
                'summary': self._create_summary(prediction, feature_vals),
                'confidence': self._estimate_confidence(prediction, feature_vals),
                'recommendation': self._generate_recommendation(prediction),
            }
            
            insights_list.append(insight)
        
        return insights_list
    
    def _create_summary(self, prediction: float, feature_values: Dict) -> str:
        """Create a short summary"""
        if len(feature_values) == 0:
            return f"Prediction: {prediction:.2f}"
        
        avg_feature = np.mean(list(feature_values.values()))
        summary = f"Based on {len(feature_values)} features, prediction is {prediction:.2f}"
        
        if prediction > avg_feature * 1.5:
            summary += " (High)"
        elif prediction < avg_feature * 0.5:
            summary += " (Low)"
        else:
            summary += " (Medium)"
        
        return summary
    
    def _estimate_confidence(self, prediction: float, feature_values: Dict) -> float:
        """Estimate prediction confidence"""
        # Simple heuristic confidence based on feature availability
        confidence = min(1.0, len(feature_values) / 10)  # Assumes ~10 features optimal
        
        # Adjust based on prediction magnitude
        if prediction == 0:
            confidence *= 0.8
        
        return float(confidence)
    
    def _generate_recommendation(self, prediction: float) -> str:
        """Generate actionable recommendation"""
        if prediction < 0.3:
            return "Consider reviewing input factors affecting this prediction."
        elif prediction > 0.7:
            return "This prediction has strong supporting evidence."
        else:
            return "This prediction is within normal range."
    
    def analyze_feature_impact(self, feature_name: str,
                              predictions_before: np.ndarray,
                              predictions_after: np.ndarray) -> Dict:
        """
        Analyze impact of changing a feature
        """
        logger.info(f"Analyzing impact of '{feature_name}'")
        
        change = np.mean(predictions_after - predictions_before)
        change_pct = (change / np.mean(np.abs(predictions_before))) * 100 if np.mean(np.abs(predictions_before)) != 0 else 0
        
        impact = {
            'feature': feature_name,
            'mean_change': float(change),
            'percent_change': float(change_pct),
            'max_change': float(np.max(predictions_after - predictions_before)),
            'min_change': float(np.min(predictions_after - predictions_before)),
            'impact_description': self._describe_impact(change_pct),
        }
        
        return impact
    
    def _describe_impact(self, percent_change: float) -> str:
        """Describe impact in business terms"""
        abs_change = abs(percent_change)
        
        if abs_change < 1:
            return "Minimal impact"
        elif abs_change < 5:
            return "Low impact"
        elif abs_change < 10:
            return "Moderate impact"
        elif abs_change < 30:
            return "Significant impact"
        else:
            return "Substantial impact"
    
    def generate_trend_analysis(self, time_series_data: pd.DataFrame,
                               date_col: str,
                               value_col: str) -> str:
        """
        Analyze trends in predictions over time
        """
        logger.info("Analyzing trends...")
        
        # Sort by date
        df = time_series_data.sort_values(date_col)
        values = df[value_col].values
        
        # Calculate trend
        early_mean = np.mean(values[:len(values)//2])
        late_mean = np.mean(values[len(values)//2:])
        trend_direction = "increasing" if late_mean > early_mean else "decreasing"
        trend_magnitude = abs(late_mean - early_mean) / early_mean * 100
        
        analysis = f"""
        TREND ANALYSIS
        ==============
        Overall trend: {trend_direction.capitalize()} by {trend_magnitude:.1f}%
        Time period: {df[date_col].min()} to {df[date_col].max()}
        Average value: {np.mean(values):.2f}
        Volatility: {np.std(values):.2f}
        
        Insight: The {value_col} has shown a {trend_direction} trend over the analyzed period.
        """
        
        return analysis
    
    def generate_anomaly_report(self, data: pd.DataFrame,
                               value_col: str,
                               threshold_std: float = 2.0) -> Dict:
        """
        Identify and describe anomalies
        """
        logger.info("Detecting anomalies...")
        
        mean = data[value_col].mean()
        std = data[value_col].std()
        
        anomalies = data[
            (np.abs(data[value_col] - mean) > threshold_std * std)
        ]
        
        report = {
            'total_records': len(data),
            'anomalies_detected': len(anomalies),
            'anomaly_percentage': float(len(anomalies) / len(data) * 100),
            'anomalies_description': f"Found {len(anomalies)} anomalies "
                                    f"({len(anomalies)/len(data)*100:.1f}% of data)",
            'details': anomalies.to_dict('records') if len(anomalies) > 0 else [],
        }
        
        return report
    
    def create_executive_summary(self, model_performance: Dict,
                                dataset_info: Dict,
                                key_findings: List[str]) -> str:
        """
        Create executive summary for stakeholders
        """
        logger.info("Creating executive summary")
        
        summary = f"""
        ════════════════════════════════════════════════════════════
        EXECUTIVE SUMMARY - ML PIPELINE ANALYSIS
        ════════════════════════════════════════════════════════════
        
        📊 DATASET OVERVIEW
        ───────────────────
        • Records: {dataset_info.get('records', 'N/A')}
        • Features: {dataset_info.get('features', 'N/A')}
        • Data Quality Score: {dataset_info.get('quality_score', 'N/A')}%
        
        🎯 MODEL PERFORMANCE
        ────────────────────
        """
        
        for metric, value in model_performance.items():
            summary += f"• {metric}: {value:.4f}\n"
        
        summary += "\n🔍 KEY FINDINGS\n───────────────\n"
        for i, finding in enumerate(key_findings, 1):
            summary += f"{i}. {finding}\n"
        
        summary += f"""
        
        📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ════════════════════════════════════════════════════════════
        """
        
        return summary
