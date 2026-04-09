"""
PHASE 10: Governance Module
Enable error logging, drift monitoring, and service health alerts
"""

import pandas as pd
import numpy as np
import logging
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class Governance:
    """
    Robust governance and monitoring:
    - Error logging and tracking
    - Model drift detection
    - Service health monitoring
    - Alerting system
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.log_dir = Path(self.config.get('log_file', 'logs')).parent
        self.log_dir.mkdir(exist_ok=True)
        
        self.error_log = []
        self.drift_metrics = []
        self.health_metrics = []
        self.alerts = []
        
        self._setup_logging()
        logger.info("Governance module initialized")
    
    def _setup_logging(self):
        """Setup comprehensive error logging"""
        log_file = self.log_dir / 'ml_pipeline.log'
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
        logger.info(f"Logging initialized to {log_file}")
    
    def log_error(self, error_type: str, message: str, 
                 context: Dict = None, severity: str = "error") -> Dict:
        """
        Log an error with context
        severity: 'info', 'warning', 'error', 'critical'
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message,
            'severity': severity,
            'context': context or {},
        }
        
        self.error_log.append(error_entry)
        
        # Also log with Python logging
        log_func = getattr(logger, severity.lower(), logger.error)
        log_func(f"{error_type}: {message}")
        
        # Trigger alert if critical
        if severity == 'critical':
            self.create_alert(
                alert_type='CRITICAL_ERROR',
                message=message,
                severity='critical'
            )
        
        return error_entry
    
    def detect_model_drift(self, 
                          historical_dist: np.ndarray,
                          current_dist: np.ndarray,
                          feature_name: str = "feature") -> Dict:
        """
        Detect statistical drift in model predictions or features
        Uses Kolmogorov-Smirnov test
        """
        logger.info(f"Checking drift for {feature_name}")
        
        from scipy import stats
        
        # Perform KS test
        ks_stat, p_value = stats.ks_2samp(historical_dist, current_dist)
        
        drift_threshold = self.config.get('drift_threshold', 0.05)
        is_drift = p_value < drift_threshold
        
        drift_info = {
            'feature': feature_name,
            'timestamp': datetime.now().isoformat(),
            'ks_statistic': float(ks_stat),
            'p_value': float(p_value),
            'drift_detected': is_drift,
            'severity': 'high' if ks_stat > 0.2 else 'medium' if is_drift else 'low',
        }
        
        self.drift_metrics.append(drift_info)
        
        if is_drift:
            logger.warning(f"Drift detected in {feature_name} (p-value: {p_value:.4f})")
            if self.config.get('enable_alerts'):
                self.create_alert(
                    alert_type='DRIFT_DETECTED',
                    message=f"Data drift detected in {feature_name}",
                    severity='warning'
                )
        
        return drift_info
    
    def monitor_prediction_latency(self, 
                                  predictions: List[float],
                                  latencies_ms: List[float]) -> Dict:
        """
        Monitor prediction latency
        """
        logger.info("Monitoring prediction latency")
        
        mean_latency = np.mean(latencies_ms)
        p99_latency = np.percentile(latencies_ms, 99)
        threshold = self.config.get('latency_threshold_ms', 100)
        
        latency_status = {
            'mean_latency_ms': float(mean_latency),
            'p99_latency_ms': float(p99_latency),
            'max_latency_ms': float(np.max(latencies_ms)),
            'threshold_ms': threshold,
            'status': 'degraded' if mean_latency > threshold else 'healthy',
            'predictions_count': len(predictions),
            'timestamp': datetime.now().isoformat(),
        }
        
        self.health_metrics.append(latency_status)
        
        if mean_latency > threshold:
            logger.warning(f"Latency degradation: {mean_latency:.2f}ms > {threshold}ms")
            if self.config.get('enable_alerts'):
                self.create_alert(
                    alert_type='LATENCY_DEGRADATION',
                    message=f"Mean latency {mean_latency:.2f}ms exceeds threshold",
                    severity='warning'
                )
        
        return latency_status
    
    def monitor_data_quality(self, data: pd.DataFrame) -> Dict:
        """
        Monitor data quality metrics
        """
        logger.info("Monitoring data quality")
        
        quality_score = 100 * (1 - (data.isna().sum().sum() / (len(data) * len(data.columns))))
        
        quality_status = {
            'timestamp': datetime.now().isoformat(),
            'quality_score': float(quality_score),
            'missing_percent': float((data.isna().sum().sum() / (len(data) * len(data.columns))) * 100),
            'rows': len(data),
            'columns': len(data.columns),
            'duplicates': int(data.duplicated().sum()),
            'status': 'excellent' if quality_score > 95 else 'good' if quality_score > 90 else 'fair' if quality_score > 80 else 'poor',
        }
        
        self.health_metrics.append(quality_status)
        
        if quality_score < 80:
            logger.warning(f"Data quality degradation: {quality_score:.1f}%")
            if self.config.get('enable_alerts'):
                self.create_alert(
                    alert_type='DATA_QUALITY_ISSUE',
                    message=f"Data quality score: {quality_score:.1f}%",
                    severity='warning'
                )
        
        return quality_status
    
    def create_alert(self, alert_type: str, message: str, 
                    severity: str = 'warning') -> Dict:
        """
        Create system alert
        severity: 'info', 'warning', 'critical'
        """
        alert = {
            'id': len(self.alerts) + 1,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'resolved': False,
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{severity.upper()}]: {alert_type} - {message}")
        
        # Send alert (mock implementation)
        if self.config.get('enable_alerts'):
            self._send_alert_notification(alert)
        
        return alert
    
    def _send_alert_notification(self, alert: Dict):
        """
        Send alert notification (email, Slack, etc.)
        This is a mock implementation
        """
        alert_email = self.config.get('alert_email', 'admin@company.com')
        logger.info(f"Sending alert notification to {alert_email}")
        # In production: integrate with email/Slack service
    
    def get_error_report(self) -> pd.DataFrame:
        """Get error log report"""
        if not self.error_log:
            return pd.DataFrame()
        
        return pd.DataFrame(self.error_log)
    
    def get_drift_report(self) -> pd.DataFrame:
        """Get drift detection report"""
        if not self.drift_metrics:
            return pd.DataFrame()
        
        return pd.DataFrame(self.drift_metrics)
    
    def get_health_report(self) -> pd.DataFrame:
        """Get health monitoring report"""
        if not self.health_metrics:
            return pd.DataFrame()
        
        return pd.DataFrame(self.health_metrics)
    
    def get_alerts(self, unresolved_only: bool = True) -> pd.DataFrame:
        """Get alerts"""
        if not self.alerts:
            return pd.DataFrame()
        
        alerts_list = self.alerts
        if unresolved_only:
            alerts_list = [a for a in alerts_list if not a['resolved']]
        
        return pd.DataFrame(alerts_list)
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False
    
    def get_governance_summary(self) -> str:
        """Get governance status summary"""
        error_count = len(self.error_log)
        drift_count = sum(1 for d in self.drift_metrics if d.get('drift_detected'))
        alert_count = len([a for a in self.alerts if not a['resolved']])
        
        summary = f"""
        GOVERNANCE & MONITORING SUMMARY
        ================================
        
        📋 ERROR TRACKING
        • Total Errors: {error_count}
        • Critical Issues: {sum(1 for e in self.error_log if e['severity'] == 'critical')}
        
        📊 DRIFT MONITORING
        • Features Monitored: {len(set(d['feature'] for d in self.drift_metrics))}
        • Drift Detected: {drift_count}
        
        🚨 ALERTS & NOTIFICATIONS
        • Active Alerts: {alert_count}
        • High Severity: {sum(1 for a in self.alerts if a['severity'] == 'critical' and not a['resolved'])}
        
        ⚙️  SYSTEM STATUS
        • Health Checks: {len(self.health_metrics)}
        • Last Check: {self.health_metrics[-1]['timestamp'] if self.health_metrics else 'N/A'}
        """
        
        return summary
    
    def export_governance_report(self) -> Dict:
        """Export complete governance report"""
        return {
            'errors': self.get_error_report().to_dict('records'),
            'drift': self.get_drift_report().to_dict('records'),
            'health': self.get_health_report().to_dict('records'),
            'alerts': self.get_alerts(unresolved_only=False).to_dict('records'),
            'summary': self.get_governance_summary(),
        }
