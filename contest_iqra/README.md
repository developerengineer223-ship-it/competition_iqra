# 🚀 Production-Ready ML Pipeline

A comprehensive, production-grade machine learning pipeline with 10 integrated phases for building, deploying, and monitoring ML models.

## 📋 Overview

This pipeline implements all 10 critical phases for production ML systems:

1. **Phase 1: Data Ingestion** - Connect to data sources and register datasets
2. **Phase 2: Data Quality** - Clean, validate, and assess data integrity
3. **Phase 3: Feature Engineering** - Automated feature creation and transformation
4. **Phase 4: Search Engine** - Dynamic filtering and result exploration
5. **Phase 5: What-If Analysis** - Prediction explanations and simulations
6. **Phase 6: Model Deployment** - Train, evaluate, and deploy models
7. **Phase 7: Visualizations** - Interactive dashboards and analytics
8. **Phase 8: Insights** - Plain-English prediction explanations
9. **Phase 9: Reporting** - Automated report generation
10. **Phase 10: Governance** - Monitoring, drift detection, and alerting

## 📁 Project Structure

```
contest_iqra/
├── ml_pipeline.py              # Main orchestrator
├── config.py                   # Pipeline configuration
├── data_ingestion.py           # Phase 1: Data loading
├── data_quality.py             # Phase 2: Data cleaning & validation
├── feature_engineering.py      # Phase 3: Feature creation
├── search_engine.py            # Phase 4: Dynamic search/filtering
├── what_if_analysis.py         # Phase 5: Explanations & simulations
├── model_deployment.py         # Phase 6: Model training & deployment
├── visualizations.py           # Phase 7: Dashboard creation
├── insights_generator.py       # Phase 8: Insight generation
├── reporting.py                # Phase 9: Report generation
├── governance.py               # Phase 10: Monitoring & governance
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone/Navigate to project**:
```bash
cd contest_iqra
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure settings** (optional):
Edit `config.py` to customize:
- Data paths and sources
- Quality thresholds
- Model parameters
- Report formats
- Governance rules

## 🚀 Quick Start

### Run the Complete Pipeline

```bash
python ml_pipeline.py
```

This executes all 10 phases sequentially with automatic error handling and reporting.

### Run Individual Phases

```python
from ml_pipeline import MLPipelineOrchestrator

pipeline = MLPipelineOrchestrator()

# Run specific phase
pipeline.phase_1_data_ingestion()
pipeline.phase_2_data_quality()
# ... etc
```

### Use Individual Components

```python
from data_ingestion import DataIngestion
from data_quality import DataQuality
from feature_engineering import FeatureEngineering

# Data ingestion
ingestion = DataIngestion()
data = ingestion._generate_synthetic_data(n_samples=1000)

# Data quality
quality = DataQuality(data)
assessment = quality.run_full_assessment()
cleaned_data = quality.get_cleaned_data()

# Feature engineering
engineer = FeatureEngineering(cleaned_data)
engineered_data = engineer.run_automated_engineering()
```

## 📊 Phase Details

### Phase 1: Data Ingestion
- Load from CSV, Parquet, Snowflake, SQL databases
- Register datasets in AI Catalog
- Metadata tracking

### Phase 2: Data Quality (The Surgeon)
- Missing value imputation
- Outlier detection and handling
- Duplicate removal
- Data leakage detection
- Automatic issue reporting

### Phase 3: Feature Engineering (The Processor)
- Polynomial feature creation
- Interaction features
- Categorical encoding (target, one-hot, label)
- Text/NLP vectorization
- Feature scaling

### Phase 4: Search Engine
- Multi-field filtering
- Range queries
- Pagination support
- Full-text search
- Dynamic result exploration

### Phase 5: What-If Analysis (The Slider)
- SHAP-based explanations
- Prediction drivers identification
- What-if scenario simulations
- Sensitivity analysis
- Feature impact quantification

### Phase 6: Model Deployment (The AI Heart)
- Multiple model training (Linear, RF, XGBoost, LightGBM)
- Automatic model selection
- Versioned model storage
- Batch prediction capability
- Model registry

### Phase 7: Visualizations (The Painter)
- Feature importance charts
- ROC curves
- Lift charts
- Prediction distributions
- Residual plots
- Model comparison
- Interactive HTML dashboard

### Phase 8: Insights (The Insights Layer)
- Prediction explanations in plain English
- Trend analysis
- Anomaly detection
- Executive summaries
- Business-actionable recommendations

### Phase 9: Automated Reporting
- HTML report generation
- Performance metrics
- Data quality summaries
- Automated scheduling ready
- Weekly/monthly reports

### Phase 10: Governance
- Comprehensive error logging
- Statistical drift detection
- Service latency monitoring
- Data quality checks
- Alert management
- Health dashboards

## 📈 Key Capabilities

### Interpretability
- ✅ SHAP value explanations
- ✅ Feature importance tracking
- ✅ Prediction drivers identification
- ✅ Plain-English summaries

### Monitoring
- ✅ Real-time drift detection
- ✅ Data quality scoring
- ✅ Latency tracking
- ✅ Error logging and alerting

### Scalability
- ✅ Batch prediction support
- ✅ Model versioning
- ✅ Distributed training ready
- ✅ Multi-model comparison

### Governance
- ✅ Comprehensive audit logs
- ✅ Model registry
- ✅ Alert notifications
- ✅ Health monitoring

## 📊 Output Files

After running the pipeline, you'll find:

```
dashboard.html                  # Interactive analytics dashboard
reports/                        # Generated HTML reports
  └── ML_Pipeline_Performance_Report_*.html
models/                         # Trained model files
  ├── best_model_v1.0.0.pkl
  └── *.pkl (versioned models)
logs/                           # Log files
  └── ml_pipeline.log
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Data Configuration
DATA_CONFIG = {
    "test_size": 0.2,           # Train/test split
    "random_state": 42,
}

# Quality Configuration
QUALITY_CONFIG = {
    "missing_value_threshold": 0.5,  # Drop columns with >50% missing
    "outlier_method": "iqr",         # Detection method
    "check_data_leakage": True,
}

# Feature Engineering
FEATURE_CONFIG = {
    "create_polynomial_features": True,
    "categorical_encoding": "target",
    "text_vectorization": "tfidf",
}

# Model Configuration
MODEL_CONFIG = {
    "models": ["linear_regression", "xgboost", "lightgbm"],
    "primary_metric": "rmse",
    "cv_folds": 5,
}

# Governance
GOVERNANCE_CONFIG = {
    "enable_logging": True,
    "enable_drift_monitoring": True,
    "drift_threshold": 0.05,
    "enable_alerts": True,
}
```

## 📋 API Reference

### Key Classes

#### DataIngestion
```python
from data_ingestion import DataIngestion

ingestion = DataIngestion()
data = ingestion.load_csv("data.csv")
ingestion.register_in_catalog("my_dataset", "description")
metadata = ingestion.get_metadata()
```

#### DataQuality
```python
from data_quality import DataQuality

quality = DataQuality(data)
assessment = quality.run_full_assessment()
cleaned_data = quality.get_cleaned_data()
report = quality.get_quality_report()
```

#### FeatureEngineering
```python
from feature_engineering import FeatureEngineering

engineer = FeatureEngineering(data, target='target_col')
engineered = engineer.run_automated_engineering()
report = engineer.get_feature_log()
```

#### SearchEngine
```python
from search_engine import SearchEngine

search = SearchEngine(predictions_df)
results = search.search_by_field('region', 'North', '==')
results = search.range_search('price', 100000, 500000)
results = search.multi_filter({'region': ('==', 'North'), 'price': ('>', 200000)})
```

#### WhatIfAnalysis
```python
from what_if_analysis import WhatIfAnalysis

whatif = WhatIfAnalysis(model, X_test, y_test)
whatif.initialize_explainer('shap')
explanation = whatif.explain_prediction(sample_idx=0)
scenario = whatif.what_if_scenario(base_sample, {'price': 300000})
```

#### ModelDeployment
```python
from model_deployment import ModelDeployment

deployer = ModelDeployment()
deployer.deploy_model(model, "my_model", version="1.0.0")
predictions = deployer.predict_batch(model, X_batch)
registry = deployer.get_model_registry()
```

#### Governance
```python
from governance import Governance

gov = Governance()
gov.monitor_data_quality(data)
gov.detect_model_drift(historical_data, current_data)
gov.log_error("ERROR_TYPE", "Error message")
report = gov.export_governance_report()
```

## 🎯 Use Cases

### Sales Forecasting
- Load historical sales data
- Engineer time-series features
- Train predictive model
- Generate what-if scenarios
- Monitor forecast drift

### Credit Risk Assessment
- Ingest customer data
- Quality checks and outlier handling
- Feature engineering for risk factors
- Deploy classification model
- Track model drift over time

### Demand Planning
- Load demand history
- Automatic feature creation
- Compare multiple models
- Generate insights and recommendations
- Export automated reports

### Customer Churn Prediction
- Data quality assessment
- Feature engineering for behavioral signals
- Train and explain predictions
- What-if analysis for retention strategies
- Monitor for concept drift

## 📝 Logging and Monitoring

All operations are logged to `logs/ml_pipeline.log`:

```
2024-04-01 10:30:15 - ml_pipeline - INFO - Starting Phase 1
2024-04-01 10:30:16 - data_ingestion - INFO - Loaded 1000 records
2024-04-01 10:30:18 - data_quality - WARNING - Found 45 outliers
```

Monitor logs in real-time:
```bash
tail -f logs/ml_pipeline.log
```

## 🚨 Error Handling

The pipeline includes robust error handling:
- Automatic error logging
- Phase-level error recovery
- Detailed error messages
- Alert notifications
- Continues with remaining phases when possible

## 🔒 Security & Governance

- ✅ Comprehensive audit logging
- ✅ Model versioning and tracking
- ✅ Data leakage detection
- ✅ Drift monitoring and alerts
- ✅ Access logging
- ✅ Error tracking

## 📞 Support & Development

### Adding New Data Sources
Edit `data_ingestion.py`:
```python
def load_from_elasticsearch(self, host, index):
    # Implement your source connection
    pass
```

### Custom Models
Add to `model_deployment.py`:
```python
def train_custom_model(self):
    # Implement your model
    pass
```

### Custom Visualizations
Add to `visualizations.py`:
```python
def custom_chart(self, data):
    # Create your visualization
    pass
```

## 📄 License

This project is provided as-is for production ML pipeline implementation.

## 🤝 Contributing

To extend the pipeline:
1. Add new functionality to appropriate phase module
2. Update `ml_pipeline.py` orchestrator if needed
3. Add configuration to `config.py`
4. Update documentation

## 📞 Contact

For questions or issues, refer to the logs and error messages which provide detailed diagnostic information.

---

**Status**: ✅ Production-Ready | **Version**: 1.0.0 | **Last Updated**: 2024-04-01
