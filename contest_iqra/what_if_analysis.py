"""
PHASE 5: What-If Analysis Module (The Slider)
Enable prediction explanations and what-if simulations
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
import shap
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class WhatIfAnalysis:
    """
    What-If simulations and prediction explanations
    - SHAP value calculations
    - Feature importance explanations
    - What-if scenario testing
    - Sensitivity analysis
    """
    
    def __init__(self, model, X_data: pd.DataFrame, y_data: pd.Series = None, config: Dict = None):
        self.model = model
        self.X_data = X_data.copy()
        self.y_data = y_data
        self.config = config or {}
        self.explainer = None
        self.shap_values = None
        self.simulations = []
        logger.info("WhatIfAnalysis initialized")
    
    def initialize_explainer(self, method: str = 'shap'):
        """Initialize explanation method"""
        logger.info(f"Initializing explainer with method: {method}")
        
        try:
            if method == 'shap':
                # Initialize SHAP explainer
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("SHAP TreeExplainer initialized")
            else:
                logger.warning(f"Method '{method}' not yet implemented")
        
        except Exception as e:
            logger.warning(f"Could not initialize SHAP: {e}. Falling back to feature importance.")
    
    def explain_prediction(self, sample_idx: int = 0) -> Dict:
        """Explain a single prediction"""
        logger.info(f"Explaining prediction for sample {sample_idx}")
        
        if sample_idx >= len(self.X_data):
            logger.error(f"Sample index {sample_idx} out of range")
            return {}
        
        sample = self.X_data.iloc[sample_idx:sample_idx+1]
        prediction = self.model.predict(sample)[0]
        
        explanation = {
            'sample_index': sample_idx,
            'prediction': float(prediction),
            'feature_values': sample.iloc[0].to_dict(),
            'feature_contributions': {},
        }
        
        try:
            # Calculate SHAP values for this sample
            if self.explainer:
                shap_values = self.explainer.shap_values(sample)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # Binary classification - take positive class
                
                # Create explanation with top contributing features
                feature_contributions = {}
                for i, feature in enumerate(self.X_data.columns):
                    feature_contributions[feature] = {
                        'shap_value': float(shap_values[0, i]),
                        'feature_value': float(sample.iloc[0, i])
                    }
                
                explanation['feature_contributions'] = feature_contributions
                explanation['base_value'] = float(self.explainer.expected_value)
        
        except Exception as e:
            logger.warning(f"Could not generate SHAP explanation: {e}")
        
        return explanation
    
    def what_if_scenario(self, base_sample: pd.DataFrame, 
                        variable_changes: Dict[str, float]) -> Dict:
        """
        Test how changing variables impacts predictions
        variable_changes: {feature_name: new_value}
        """
        logger.info(f"Running what-if scenario with changes: {variable_changes}")
        
        original_prediction = self.model.predict(base_sample)[0]
        
        # Create modified sample
        modified_sample = base_sample.copy()
        for var, new_value in variable_changes.items():
            if var in modified_sample.columns:
                modified_sample[var] = new_value
        
        modified_prediction = self.model.predict(modified_sample)[0]
        
        scenario = {
            'original_prediction': float(original_prediction),
            'modified_prediction': float(modified_prediction),
            'prediction_change': float(modified_prediction - original_prediction),
            'percent_change': float((modified_prediction - original_prediction) / original_prediction * 100) if original_prediction != 0 else 0,
            'variables_changed': variable_changes,
            'original_values': base_sample.iloc[0].to_dict(),
            'modified_values': modified_sample.iloc[0].to_dict(),
        }
        
        self.simulations.append(scenario)
        logger.info(f"What-if simulation complete: {scenario['percent_change']:.2f}% change")
        
        return scenario
    
    def sensitivity_analysis(self, feature: str, base_sample: pd.DataFrame, 
                           values: List[float]) -> pd.DataFrame:
        """
        Test sensitivity of predictions to changes in a specific feature
        """
        logger.info(f"Running sensitivity analysis for feature: {feature}")
        
        results = []
        
        for value in values:
            modified_sample = base_sample.copy()
            modified_sample[feature] = value
            
            prediction = self.model.predict(modified_sample)[0]
            results.append({
                'feature': feature,
                'value': value,
                'prediction': prediction,
            })
        
        results_df = pd.DataFrame(results)
        logger.info(f"Sensitivity analysis complete: {len(results)} data points")
        
        return results_df
    
    def feature_importance(self) -> Dict:
        """Get feature importance from model"""
        logger.info("Calculating feature importance")
        
        feature_importance = {}
        
        try:
            # Try to get feature importances from model
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                features = self.X_data.columns.tolist()
                
                for feat, imp in zip(features, importances):
                    feature_importance[feat] = float(imp)
                
                # Sort by importance
                feature_importance = dict(sorted(
                    feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                ))
            
            elif hasattr(self.model, 'coef_'):
                # Linear model coefficients
                coefs = np.abs(self.model.coef_)
                features = self.X_data.columns.tolist()
                
                for feat, coef in zip(features, coefs):
                    feature_importance[feat] = float(coef)
                
                feature_importance = dict(sorted(
                    feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                ))
        
        except Exception as e:
            logger.warning(f"Could not calculate feature importance: {e}")
        
        return feature_importance
    
    def get_top_driving_factors(self, sample_idx: int, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get top factors driving a prediction"""
        explanation = self.explain_prediction(sample_idx)
        
        if not explanation.get('feature_contributions'):
            return []
        
        contributions = explanation['feature_contributions']
        # Sort by absolute SHAP value
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]['shap_value']),
            reverse=True
        )
        
        return [(feat, data['shap_value']) for feat, data in sorted_features[:top_n]]
    
    def generate_explanation_text(self, sample_idx: int) -> str:
        """Generate plain-English explanation of a prediction"""
        explanation = self.explain_prediction(sample_idx)
        
        if not explanation:
            return "Could not generate explanation"
        
        text = f"""
        PREDICTION EXPLANATION
        ======================
        Sample Index: {explanation['sample_index']}
        Prediction Value: {explanation['prediction']:.4f}
        
        Top Contributing Factors:
        """
        
        if explanation.get('feature_contributions'):
            contributions = explanation['feature_contributions']
            sorted_features = sorted(
                contributions.items(),
                key=lambda x: abs(x[1]['shap_value']),
                reverse=True
            )[:5]
            
            for feat, data in sorted_features:
                impact = "increased" if data['shap_value'] > 0 else "decreased"
                text += f"\n  • {feat}: {data['feature_value']:.4f} ({impact} prediction by {abs(data['shap_value']):.4f})"
        
        return text
    
    def get_simulation_results(self) -> pd.DataFrame:
        """Get all what-if simulation results"""
        if not self.simulations:
            return pd.DataFrame()
        
        return pd.DataFrame([
            {
                'scenario': i,
                'original': sim['original_prediction'],
                'modified': sim['modified_prediction'],
                'change': sim['prediction_change'],
                'percent_change': sim['percent_change'],
            }
            for i, sim in enumerate(self.simulations)
        ])
