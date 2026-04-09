"""
PHASE 7: Visualizations Module (The Painter)
Build comprehensive analytics dashboard with charts and insights
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.metrics import roc_curve, auc
import json

logger = logging.getLogger(__name__)


class Visualizations:
    """
    Create comprehensive visual analytics dashboard
    - Feature importance charts
    - ROC curves
    - Lift charts
    - Prediction distributions
    - Model comparison
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.figures = {}
        logger.info("Visualizations initialized")
    
    def feature_importance_chart(self, feature_importance: Dict, 
                                title: str = "Feature Importance") -> go.Figure:
        """Create feature importance bar chart"""
        logger.info("Creating feature importance chart")
        
        features = list(feature_importance.keys())[:15]  # Top 15
        importances = [feature_importance[f] for f in features]
        
        fig = go.Figure(data=[
            go.Bar(
                x=importances,
                y=features,
                orientation='h',
                marker=dict(color=importances, colorscale='Viridis'),
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Importance",
            yaxis_title="Feature",
            height=600,
            hovermode='closest',
        )
        
        self.figures['feature_importance'] = fig
        return fig
    
    def roc_curve_chart(self, y_true, y_pred_proba) -> go.Figure:
        """Create ROC curve"""
        logger.info("Creating ROC curve")
        
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        fig = go.Figure(data=[
            go.Scatter(
                x=fpr, y=tpr,
                mode='lines',
                name=f'ROC (AUC = {roc_auc:.3f})',
                line=dict(color='darkorange', width=2),
            ),
            go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                name='Random Classifier',
                line=dict(color='navy', width=2, dash='dash'),
            )
        ])
        
        fig.update_layout(
            title='ROC Curve',
            xaxis_title='False Positive Rate',
            yaxis_title='True Positive Rate',
            hovermode='closest',
            width=700, height=700,
        )
        
        self.figures['roc_curve'] = fig
        return fig
    
    def lift_chart(self, y_true, y_pred_proba, n_bins: int = 10) -> go.Figure:
        """Create lift chart"""
        logger.info("Creating lift chart")
        
        # Calculate lift for each decile
        df = pd.DataFrame({
            'actual': y_true,
            'predicted': y_pred_proba
        })
        
        df['decile'] = pd.qcut(df['predicted'], q=n_bins, duplicates='drop')
        
        lift_data = []
        for decile in sorted(df['decile'].unique(), reverse=True):
            decile_df = df[df['decile'] == decile]
            lift = decile_df['actual'].mean() / df['actual'].mean()
            lift_data.append({
                'decile': str(decile),
                'lift': lift,
                'count': len(decile_df)
            })
        
        lift_df = pd.DataFrame(lift_data)
        
        fig = go.Figure(data=[
            go.Bar(
                x=lift_df['decile'],
                y=lift_df['lift'],
                marker_color='lightblue',
            ),
            go.Scatter(
                x=lift_df['decile'],
                y=[1] * len(lift_df),
                mode='lines',
                name='Baseline',
                line=dict(color='red', dash='dash'),
            )
        ])
        
        fig.update_layout(
            title='Lift Chart by Decile',
            xaxis_title='Decile',
            yaxis_title='Lift',
            height=500,
        )
        
        self.figures['lift_chart'] = fig
        return fig
    
    def prediction_distribution(self, y_true: pd.Series, 
                               y_pred: np.ndarray) -> go.Figure:
        """Create prediction distribution chart"""
        logger.info("Creating prediction distribution")
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Actual Distribution", "Predicted Distribution")
        )
        
        fig.add_trace(
            go.Histogram(x=y_true, name='Actual', opacity=0.7, nbinsx=30),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Histogram(x=y_pred, name='Predicted', opacity=0.7, nbinsx=30),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text="Value", row=1, col=1)
        fig.update_xaxes(title_text="Value", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        
        fig.update_layout(height=400, showlegend=False)
        
        self.figures['prediction_distribution'] = fig
        return fig
    
    def residual_plot(self, y_true: pd.Series, y_pred: np.ndarray) -> go.Figure:
        """Create residual plot"""
        logger.info("Creating residual plot")
        
        residuals = y_true - y_pred
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Residuals vs Predicted", "Residuals Distribution")
        )
        
        fig.add_trace(
            go.Scatter(
                x=y_pred,
                y=residuals,
                mode='markers',
                marker=dict(size=5, color='blue', opacity=0.6),
                name='Residuals'
            ),
            row=1, col=1
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
        
        fig.add_trace(
            go.Histogram(x=residuals, nbinsx=30, name='Distribution'),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text="Predicted Values", row=1, col=1)
        fig.update_yaxes(title_text="Residuals", row=1, col=1)
        fig.update_xaxes(title_text="Residuals", row=1, col=2)
        
        fig.update_layout(height=400, showlegend=True)
        
        self.figures['residual_plot'] = fig
        return fig
    
    def model_comparison(self, metrics: Dict[str, Dict]) -> go.Figure:
        """Create model comparison chart"""
        logger.info("Creating model comparison")
        
        models = list(metrics.keys())
        
        # Get primary metric for comparison
        metric_key = list(metrics[models[0]].keys())[0]
        values = [metrics[model].get(metric_key, 0) for model in models]
        
        fig = go.Figure(data=[
            go.Bar(
                x=models,
                y=values,
                marker=dict(color=values, colorscale='RdYlGn'),
            )
        ])
        
        fig.update_layout(
            title=f'Model Comparison ({metric_key})',
            xaxis_title='Model',
            yaxis_title=metric_key,
            height=400,
        )
        
        self.figures['model_comparison'] = fig
        return fig
    
    def confusion_matrix_heatmap(self, cm: np.ndarray, 
                                labels: List[str] = None) -> go.Figure:
        """Create confusion matrix heatmap"""
        logger.info("Creating confusion matrix heatmap")
        
        if labels is None:
            labels = [f'Class {i}' for i in range(cm.shape[0])]
        
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            colorscale='Blues',
            text=cm,
            texttemplate='%{text}',
            textfont={"size": 12},
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title='Predicted',
            yaxis_title='Actual',
            height=500,
        )
        
        self.figures['confusion_matrix'] = fig
        return fig
    
    def get_all_figures(self) -> Dict:
        """Get all created figures"""
        return self.figures
    
    def export_dashboard_html(self, output_path: str = 'dashboard.html'):
        """Export all figures to interactive HTML dashboard"""
        logger.info(f"Exporting dashboard to {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    <title>ML Pipeline Dashboard</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .container { max-width: 1400px; margin: 0 auto; }
                        .chart { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
                        h1 { color: #333; }
                        h2 { color: #666; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }
                        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🎨 ML Pipeline - Visual Analytics Dashboard</h1>
                """)
                
                for fig_name, fig in self.figures.items():
                    f.write(f"""
                    <div class="chart">
                        <h2>{fig_name.replace('_', ' ').title()}</h2>
                        {fig.to_html(include_plotlyjs=False, div_id=fig_name)}
                    </div>
                    """)
                
                f.write("""
                    </div>
                </body>
                </html>
                """)
            
            logger.info(f"Dashboard exported to {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to export dashboard: {e}")
            return None
