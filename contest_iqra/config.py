"""
Configuration Module - Centralized settings for ML Pipeline
"""

# Data Configuration
DATA_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "validation_split": 0.1,
}

# Quality Configuration
QUALITY_CONFIG = {
    "missing_value_threshold": 0.5,  # Drop columns with >50% missing
    "outlier_method": "iqr",  # Options: 'iqr', 'zscore'
    "outlier_threshold": 3,
    "check_data_leakage": True,
}

# Feature Engineering Configuration
FEATURE_CONFIG = {
    "create_polynomial_features": True,
    "polynomial_degree": 2,
    "interaction_features": True,
    "categorical_encoding": "target",  # Options: 'onehot', 'label', 'target'
    "text_vectorization": "tfidf",  # Options: 'tfidf', 'count'
    "handle_categorical": True,
}

# Model Configuration
MODEL_CONFIG = {
    "models": ["linear_regression", "xgboost", "lightgbm"],
    "primary_metric": "rmse",  # Options: 'rmse', 'mae', 'r2', 'logloss'
    "cv_folds": 5,
    "hyperparameter_tuning": True,
}

# Deployment Configuration
DEPLOYMENT_CONFIG = {
    "model_save_path": "models/",
    "enable_versioning": True,
    "prediction_batch_size": 1000,
    "latency_threshold_ms": 100,
}

# Search Configuration
SEARCH_CONFIG = {
    "enable_filters": True,
    "page_size": 20,
    "searchable_fields": ["price", "sqft", "bedrooms", "neighborhood", "condition"],
}

# Visualization Configuration
VIZ_CONFIG = {
    "theme": "plotly_white",
    "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
}

# Governance Configuration
GOVERNANCE_CONFIG = {
    "enable_logging": True,
    "log_file": "logs/pipeline.log",
    "enable_drift_monitoring": True,
    "drift_threshold": 0.05,
    "enable_alerts": True,
    "alert_email": "admin@company.com",
}

# Reporting Configuration
REPORTING_CONFIG = {
    "report_format": "pdf",
    "report_frequency": "weekly",
    "output_dir": "reports/",
    "include_sections": [
        "executive_summary",
        "model_performance",
        "feature_importance",
        "predictions_sample",
        "data_quality",
        "governance_status",
    ]
}

# Search Configuration
SEARCH_CONFIG = {
    "max_results": 100,
    "enable_pagination": True,
    "searchable_fields": ["predictions", "actuals", "residuals"],
}

# What-If Configuration
WHATIF_CONFIG = {
    "enable_explanations": True,
    "explanation_method": "shap",  # Options: 'shap', 'lime', 'permutation'
    "num_simulations": 100,
}
