"""
PHASE 2: Data Quality Assessment Module (The Surgeon)
Handles missing values, outliers, data validation, and leakage detection
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from scipy import stats

logger = logging.getLogger(__name__)


class DataQuality:
    """
    Comprehensive data quality assessment and cleaning
    - Handle missing values
    - Detect and isolate outliers
    - Check for data leakage
    - Validate data integrity
    """
    
    def __init__(self, data: pd.DataFrame, config: Dict = None):
        self.data = data.copy()
        self.original_data = data.copy()
        self.config = config or {}
        self.quality_report = {}
        self.issues = []
        logger.info(f"DataQuality initialized with {data.shape[0]} rows and {data.shape[1]} columns")
    
    def run_full_assessment(self) -> Dict:
        """Run complete quality assessment"""
        logger.info("Starting full data quality assessment...")
        
        assessment = {
            "missing_values": self._assess_missing_values(),
            "outliers": self._detect_outliers(),
            "data_leakage": self._check_data_leakage(),
            "duplicates": self._check_duplicates(),
            "data_types": self._validate_data_types(),
            "issues_summary": self.issues,
        }
        
        self.quality_report = assessment
        logger.info(f"Quality assessment complete. Found {len(self.issues)} issues.")
        return assessment
    
    def _assess_missing_values(self) -> Dict:
        """Assess and handle missing values"""
        logger.info("Assessing missing values...")
        missing_report = {}
        
        missing_threshold = self.config.get('missing_value_threshold', 0.5)
        
        for col in self.data.columns:
            missing_pct = self.data[col].isna().sum() / len(self.data)
            missing_report[col] = {
                "count": self.data[col].isna().sum(),
                "percentage": round(missing_pct * 100, 2),
                "action": "drop" if missing_pct > missing_threshold else "impute"
            }
            
            if missing_pct > 0:
                if missing_pct > missing_threshold:
                    logger.warning(f"Column '{col}' has {missing_pct*100:.2f}% missing - dropping")
                    self.data = self.data.drop(col, axis=1)
                    self.issues.append(f"Dropped column '{col}' ({missing_pct*100:.2f}% missing)")
                else:
                    # Impute missing values
                    if self.data[col].dtype in ['float64', 'int64']:
                        self.data[col].fillna(self.data[col].median(), inplace=True)
                        self.issues.append(f"Imputed '{col}' with median")
                    else:
                        self.data[col].fillna(self.data[col].mode()[0] if len(self.data[col].mode()) > 0 else "Unknown", inplace=True)
                        self.issues.append(f"Imputed '{col}' with mode")
        
        return missing_report
    
    def _detect_outliers(self) -> Dict:
        """Detect and handle outliers using IQR or Z-score method"""
        logger.info("Detecting outliers...")
        outlier_report = {}
        outlier_method = self.config.get('outlier_method', 'iqr')
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if outlier_method == 'iqr':
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = (self.data[col] < lower_bound) | (self.data[col] > upper_bound)
            else:  # zscore
                threshold = self.config.get('outlier_threshold', 3)
                outliers = np.abs(stats.zscore(self.data[col].dropna())) > threshold
            
            outlier_count = outliers.sum()
            outlier_report[col] = {
                "count": outlier_count,
                "percentage": round(outlier_count / len(self.data) * 100, 2),
                "bounds": [Q1 - 1.5*IQR, Q3 + 1.5*IQR] if outlier_method == 'iqr' else None
            }
            
            if outlier_count > 0:
                # Cap outliers instead of removing
                self.data.loc[self.data[col] < lower_bound, col] = lower_bound
                self.data.loc[self.data[col] > upper_bound, col] = upper_bound
                self.issues.append(f"Capped {outlier_count} outliers in '{col}'")
                logger.info(f"Found {outlier_count} outliers in '{col}'")
        
        return outlier_report
    
    def _check_data_leakage(self) -> Dict:
        """Check for potential data leakage"""
        logger.info("Checking for data leakage...")
        leakage_report = {
            "potential_leakage": [],
            "high_correlation_features": [],
        }
        
        # Check for highly correlated features (potential redundancy/leakage)
        numeric_data = self.data.select_dtypes(include=[np.number])
        if numeric_data.shape[1] > 1:
            corr_matrix = numeric_data.corr().abs()
            high_corr_pairs = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if corr_matrix.iloc[i, j] > 0.95:
                        pair = (corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j])
                        high_corr_pairs.append(pair)
                        self.issues.append(f"High correlation detected: {pair[0]} <-> {pair[1]} ({pair[2]:.3f})")
            
            leakage_report["high_correlation_features"] = high_corr_pairs
        
        # Check for suspicious patterns (e.g., perfect correlation with target-like patterns)
        leakage_report["status"] = "checked"
        logger.info("Data leakage check complete")
        
        return leakage_report
    
    def _check_duplicates(self) -> Dict:
        """Check for duplicate rows"""
        logger.info("Checking for duplicates...")
        duplicates_report = {
            "total_duplicates": self.data.duplicated().sum(),
            "percentage": round(self.data.duplicated().sum() / len(self.data) * 100, 2),
            "action": "removed" if self.data.duplicated().sum() > 0 else "none"
        }
        
        if self.data.duplicated().sum() > 0:
            dup_count = self.data.duplicated().sum()
            self.data = self.data.drop_duplicates()
            self.issues.append(f"Removed {dup_count} duplicate rows")
            logger.info(f"Removed {dup_count} duplicate rows")
        
        return duplicates_report
    
    def _validate_data_types(self) -> Dict:
        """Validate data types"""
        logger.info("Validating data types...")
        type_report = {}
        
        for col in self.data.columns:
            dtype = str(self.data[col].dtype)
            type_report[col] = {
                "type": dtype,
                "unique_values": self.data[col].nunique(),
                "is_numeric": self.data[col].dtype in ['float64', 'int64'],
            }
        
        return type_report
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """Return cleaned data"""
        return self.data.copy()
    
    def get_quality_report(self) -> Dict:
        """Return quality assessment report"""
        return self.quality_report
    
    def get_issues(self) -> List[str]:
        """Return list of issues found and actions taken"""
        return self.issues
    
    def summary_statistics(self) -> str:
        """Generate summary of data quality"""
        summary = f"""
        DATA QUALITY SUMMARY
        ====================
        Original Rows: {len(self.original_data)}
        Cleaned Rows: {len(self.data)}
        Rows Removed: {len(self.original_data) - len(self.data)}
        
        Issues Found: {len(self.issues)}
        {chr(10).join([f"  • {issue}" for issue in self.issues[:10]])}
        
        Data Shape: {self.data.shape[0]} rows × {self.data.shape[1]} columns
        """
        return summary
