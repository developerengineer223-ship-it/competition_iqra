"""
PHASE 9: Reporting Module
Automate PDF report generation for leadership
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ReportingEngine:
    """
    Generate comprehensive PDF reports for stakeholders
    - Executive summaries
    - Performance metrics
    - Visualizations
    - Recommendations
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.output_dir = Path(self.config.get('output_dir', 'reports'))
        self.output_dir.mkdir(exist_ok=True)
        self.report_data = {}
        logger.info("ReportingEngine initialized")
    
    def create_html_report(self, 
                          title: str,
                          sections: Dict[str, Any],
                          metadata: Dict = None) -> str:
        """
        Create comprehensive HTML report
        sections: {section_name: content, ...}
        """
        logger.info(f"Creating HTML report: {title}")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        # Build HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 40px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                header {{
                    border-bottom: 3px solid #0066cc;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                }}
                h1 {{
                    color: #0066cc;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                .report-meta {{
                    color: #666;
                    font-size: 0.9em;
                }}
                .metadata {{
                    background-color: #f0f0f0;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    font-size: 0.9em;
                }}
                .section {{
                    margin-bottom: 40px;
                    padding: 20px;
                    border-left: 4px solid #0066cc;
                    background-color: #f9f9f9;
                }}
                .section h2 {{
                    color: #0066cc;
                    margin-bottom: 15px;
                    font-size: 1.8em;
                }}
                .section h3 {{
                    color: #333;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }}
                .metric {{
                    display: inline-block;
                    background-color: white;
                    padding: 15px 20px;
                    margin: 10px 10px 10px 0;
                    border-radius: 5px;
                    border: 1px solid #ddd;
                    min-width: 200px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 1.8em;
                    color: #0066cc;
                    font-weight: bold;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    color: #666;
                    margin-top: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th {{
                    background-color: #0066cc;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .chart {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: white;
                    border-radius: 5px;
                }}
                .recommendation {{
                    background-color: #e8f4f8;
                    border-left: 4px solid #0066cc;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 3px;
                }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .danger {{ color: #dc3545; }}
                footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>📊 {title}</h1>
                    <div class="report-meta">
                        Generated on {timestamp}
                    </div>
                </header>
        """
        
        # Add metadata if provided
        if metadata:
            html_content += """
            <div class="metadata">
                <strong>Report Metadata:</strong><br>
            """
            for key, value in metadata.items():
                html_content += f"<strong>{key}:</strong> {value}<br>"
            html_content += "</div>"
        
        # Add sections
        for section_name, content in sections.items():
            html_content += f"""
            <div class="section">
                <h2>{section_name}</h2>
            """
            
            # Handle different content types
            if isinstance(content, pd.DataFrame):
                html_content += content.to_html(classes='table')
            elif isinstance(content, dict):
                # Create metrics display
                for key, value in content.items():
                    if isinstance(value, (int, float)):
                        html_content += f"""
                        <div class="metric">
                            <div class="metric-value">{value:.4f}</div>
                            <div class="metric-label">{key}</div>
                        </div>
                        """
                    else:
                        html_content += f"<p><strong>{key}:</strong> {value}</p>"
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        html_content += f"<div class='recommendation'>{item}</div>"
                    else:
                        html_content += f"<p>{item}</p>"
            else:
                html_content += f"<p>{content}</p>"
            
            html_content += "</div>"
        
        # Footer
        html_content += f"""
                <footer>
                    <p>This report was automatically generated by the ML Pipeline Engine.</p>
                    <p>For questions or feedback, please contact the Data Science team.</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Save report
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Report saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return ""
    
    def create_performance_report(self, 
                                 model_metrics: Dict,
                                 data_quality: Dict,
                                 predictions: pd.DataFrame = None) -> str:
        """
        Create performance report
        """
        logger.info("Creating performance report")
        
        sections = {
            "Executive Summary": f"""
            This report presents the performance metrics and quality assessment 
            of the machine learning model trained on the provided dataset. 
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """,
            
            "Model Performance": model_metrics,
            
            "Data Quality Metrics": data_quality,
        }
        
        if predictions is not None:
            sections["Prediction Sample"] = predictions.head(10)
        
        return self.create_html_report(
            "ML Pipeline Performance Report",
            sections,
            metadata={
                "Model Type": "Regression/Classification",
                "Data Points": len(predictions) if predictions is not None else "N/A",
                "Features": model_metrics.get("feature_count", "N/A"),
            }
        )
    
    def create_weekly_report(self,
                            weekly_data: Dict[str, Any]) -> str:
        """
        Create weekly performance report for leadership
        """
        logger.info("Creating weekly report")
        
        sections = {
            "Weekly Summary": f"""
            This report summarizes the performance of the ML pipeline for the week of {weekly_data.get('week', 'N/A')}.
            """,
            
            "Key Metrics": {
                "Total Predictions": weekly_data.get('total_predictions', 0),
                "Avg Model Confidence": weekly_data.get('avg_confidence', 0),
                "Data Quality Score": weekly_data.get('data_quality', 0),
                "System Uptime": f"{weekly_data.get('uptime', 0)}%",
            },
            
            "Performance Trends": weekly_data.get('trends', "No trend data available"),
            
            "Issues & Recommendations": weekly_data.get('issues', []),
        }
        
        return self.create_html_report(
            "Weekly ML Pipeline Report",
            sections,
            metadata={
                "Report Period": weekly_data.get('week', 'N/A'),
                "Generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        )
    
    def generate_summary_statistics(self, data: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for a dataset
        """
        logger.info("Generating summary statistics")
        
        numeric_data = data.select_dtypes(include=[np.number])
        
        stats = {
            "Row Count": len(data),
            "Column Count": len(data.columns),
            "Missing Values %": round((data.isna().sum().sum() / (len(data) * len(data.columns))) * 100, 2),
            "Numeric Columns": len(numeric_data.columns),
            "Categorical Columns": len(data.columns) - len(numeric_data.columns),
        }
        
        return stats
    
    def export_report_list(self) -> pd.DataFrame:
        """
        Get list of all generated reports
        """
        logger.info("Listing generated reports")
        
        reports = []
        for file in self.output_dir.glob('*.html'):
            reports.append({
                'filename': file.name,
                'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                'size_kb': round(file.stat().st_size / 1024, 2),
            })
        
        return pd.DataFrame(reports)
