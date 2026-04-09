"""
PHASE 6: Model Deployment Module (The AI Heart)
Identify top-performing models and deploy to production
"""

import pandas as pd
import numpy as np
import logging
import joblib
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime
from pathlib import Path
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report,
    log_loss
)

logger = logging.getLogger(__name__)


class ModelTraining:
    """Train multiple models and evaluate performance"""
    
    def __init__(self, X_train, X_test, y_train, y_test, 
                 task_type: str = 'regression', config: Dict = None):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.task_type = task_type
        self.config = config or {}
        self.models = {}
        self.metrics = {}
        logger.info(f"ModelTraining initialized - Task: {task_type}")
    
    def train_models(self) -> Dict[str, Any]:
        """Train multiple models and evaluate"""
        logger.info("Training models...")
        
        if self.task_type == 'regression':
            self._train_regression_models()
        else:
            self._train_classification_models()
        
        logger.info(f"Trained {len(self.models)} models")
        return self.metrics
    
    def _train_regression_models(self):
        """Train regression models"""
        logger.info("Training regression models...")
        
        # Linear Regression
        try:
            lr = LinearRegression()
            lr.fit(self.X_train, self.y_train)
            self.models['linear_regression'] = lr
            self._evaluate_regression(lr, 'linear_regression')
        except Exception as e:
            logger.warning(f"Linear Regression error: {e}")
        
        # Random Forest
        try:
            rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            rf.fit(self.X_train, self.y_train)
            self.models['random_forest'] = rf
            self._evaluate_regression(rf, 'random_forest')
        except Exception as e:
            logger.warning(f"Random Forest error: {e}")
        
        # XGBoost
        try:
            xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
            xgb_model.fit(self.X_train, self.y_train, verbose=False)
            self.models['xgboost'] = xgb_model
            self._evaluate_regression(xgb_model, 'xgboost')
        except Exception as e:
            logger.warning(f"XGBoost error: {e}")
        
        # LightGBM
        try:
            lgb_model = lgb.LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
            lgb_model.fit(self.X_train, self.y_train)
            self.models['lightgbm'] = lgb_model
            self._evaluate_regression(lgb_model, 'lightgbm')
        except Exception as e:
            logger.warning(f"LightGBM error: {e}")
    
    def _train_classification_models(self):
        """Train classification models"""
        logger.info("Training classification models...")
        
        # Logistic Regression
        try:
            lr = LogisticRegression(max_iter=1000, random_state=42)
            lr.fit(self.X_train, self.y_train)
            self.models['logistic_regression'] = lr
            self._evaluate_classification(lr, 'logistic_regression')
        except Exception as e:
            logger.warning(f"Logistic Regression error: {e}")
        
        # Random Forest
        try:
            rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            rf.fit(self.X_train, self.y_train)
            self.models['random_forest'] = rf
            self._evaluate_classification(rf, 'random_forest')
        except Exception as e:
            logger.warning(f"Random Forest error: {e}")
        
        # XGBoost
        try:
            xgb_model = xgb.XGBClassifier(n_estimators=100, random_state=42, verbosity=0, use_label_encoder=False)
            xgb_model.fit(self.X_train, self.y_train, verbose=False)
            self.models['xgboost'] = xgb_model
            self._evaluate_classification(xgb_model, 'xgboost')
        except Exception as e:
            logger.warning(f"XGBoost error: {e}")
    
    def _evaluate_regression(self, model, model_name: str):
        """Evaluate regression model"""
        y_pred = model.predict(self.X_test)
        
        self.metrics[model_name] = {
            'rmse': float(np.sqrt(mean_squared_error(self.y_test, y_pred))),
            'mae': float(mean_absolute_error(self.y_test, y_pred)),
            'r2': float(r2_score(self.y_test, y_pred)),
            'mape': float(np.mean(np.abs((self.y_test - y_pred) / self.y_test)) * 100),
        }
        
        logger.info(f"{model_name}: RMSE={self.metrics[model_name]['rmse']:.4f}")
    
    def _evaluate_classification(self, model, model_name: str):
        """Evaluate classification model"""
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]
        
        self.metrics[model_name] = {
            'auc': float(roc_auc_score(self.y_test, y_pred_proba)),
            'logloss': float(log_loss(self.y_test, y_pred_proba)),
            'accuracy': float((y_pred == self.y_test).mean()),
        }
        
        logger.info(f"{model_name}: AUC={self.metrics[model_name]['auc']:.4f}")
    
    def get_best_model(self, metric: str = 'rmse') -> Tuple[str, Any]:
        """Get best performing model"""
        if not self.metrics:
            return None, None
        
        # Find best model by metric
        best_model_name = min(
            self.metrics.keys(),
            key=lambda x: self.metrics[x].get(metric, float('inf'))
        )
        
        best_model = self.models[best_model_name]
        logger.info(f"Best model: {best_model_name} ({metric}={self.metrics[best_model_name][metric]:.4f})")
        
        return best_model_name, best_model
    
    def get_metrics(self) -> Dict:
        """Get all model metrics"""
        return self.metrics


class ModelDeployment:
    """Deploy and manage models in production"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.deployed_models = {}
        self.model_registry = []
        self.save_path = Path(self.config.get('model_save_path', 'models'))
        self.save_path.mkdir(exist_ok=True)
        logger.info("ModelDeployment initialized")
    
    def deploy_model(self, model, model_name: str, version: str = '1.0.0',
                    metadata: Dict = None) -> Dict:
        """Deploy a trained model to production"""
        logger.info(f"Deploying model: {model_name} v{version}")
        
        deployment_info = {
            'model_name': model_name,
            'version': version,
            'deployment_timestamp': datetime.now().isoformat(),
            'status': 'deployed',
            'metadata': metadata or {},
        }
        
        # Save model
        model_path = self.save_path / f"{model_name}_v{version}.pkl"
        try:
            joblib.dump(model, model_path)
            deployment_info['model_path'] = str(model_path)
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            deployment_info['status'] = 'failed'
            return deployment_info
        
        # Save metadata
        metadata_path = self.save_path / f"{model_name}_v{version}_metadata.json"
        try:
            with open(metadata_path, 'w') as f:
                json.dump(deployment_info, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")
        
        # Register in model registry
        self.deployed_models[f"{model_name}_v{version}"] = model
        self.model_registry.append(deployment_info)
        
        logger.info(f"Model deployed successfully: {model_name} v{version}")
        return deployment_info
    
    def load_model(self, model_path: str):
        """Load a model from disk"""
        try:
            model = joblib.load(model_path)
            logger.info(f"Loaded model from {model_path}")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
    
    def predict_batch(self, model, X_batch: pd.DataFrame) -> np.ndarray:
        """Make batch predictions"""
        try:
            predictions = model.predict(X_batch)
            logger.info(f"Made {len(predictions)} predictions")
            return predictions
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return np.array([])
    
    def get_model_registry(self) -> pd.DataFrame:
        """Get model registry"""
        if not self.model_registry:
            return pd.DataFrame()
        
        registry_df = pd.DataFrame([
            {
                'model_name': entry['model_name'],
                'version': entry['version'],
                'deployment_timestamp': entry['deployment_timestamp'],
                'status': entry['status'],
            }
            for entry in self.model_registry
        ])
        
        return registry_df
