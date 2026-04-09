"""
PHASE 3: Feature Engineering Module (The Processor)
Handles automated feature creation, categorical encoding, and NLP vectorization
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from category_encoders import TargetEncoder, OneHotEncoder
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class FeatureEngineering:
    """
    Automated feature engineering including:
    - Polynomial feature creation
    - Interaction features
    - Categorical encoding
    - Text/NLP vectorization
    """
    
    def __init__(self, data: pd.DataFrame, target: str = None, config: Dict = None):
        self.data = data.copy()
        self.original_data = data.copy()
        self.target = target
        self.config = config or {}
        self.feature_log = []
        self.encoders = {}
        self.text_vectorizers = {}
        logger.info("FeatureEngineering initialized")
    
    def run_automated_engineering(self, target_var: str = None) -> pd.DataFrame:
        """Run complete automated feature engineering pipeline"""
        logger.info("Starting automated feature engineering...")
        
        self.target = target_var or self.target
        
        # Separate numeric and categorical columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        
        # Remove target if it's in the feature list
        if self.target and self.target in numeric_cols:
            numeric_cols.remove(self.target)
        if self.target and self.target in categorical_cols:
            categorical_cols.remove(self.target)
        
        logger.info(f"Numeric columns: {numeric_cols}")
        logger.info(f"Categorical columns: {categorical_cols}")
        
        # Create polynomial features
        if self.config.get('create_polynomial_features', True) and numeric_cols:
            self._create_polynomial_features(numeric_cols)
        
        # Handle categorical variables
        if categorical_cols:
            self._encode_categorical(categorical_cols)
        
        # Create interaction features
        if self.config.get('interaction_features', True) and numeric_cols:
            self._create_interaction_features(numeric_cols)
        
        # Handle NLP/Text features
        text_cols = self._identify_text_columns(categorical_cols)
        if text_cols:
            self._vectorize_text(text_cols)
        
        # Scale numeric features
        self._scale_numeric_features(numeric_cols)
        
        logger.info(f"Feature engineering complete. Final shape: {self.data.shape}")
        return self.data.copy()
    
    def _create_polynomial_features(self, numeric_cols: List[str]):
        """Create polynomial features from numeric columns"""
        logger.info(f"Creating polynomial features from {len(numeric_cols)} columns...")
        
        degree = self.config.get('polynomial_degree', 2)
        
        # Create squared terms for top numeric features
        for col in numeric_cols[:min(5, len(numeric_cols))]:  # Limit to avoid explosion
            self.data[f'{col}_squared'] = self.data[col] ** 2
            self.data[f'{col}_sqrt'] = np.sqrt(np.abs(self.data[col]))
            self.feature_log.append(f"Created polynomial features for '{col}'")
        
        logger.info(f"Created {len(numeric_cols)*2} polynomial features")
    
    def _encode_categorical(self, categorical_cols: List[str]):
        """Encode categorical variables"""
        logger.info(f"Encoding {len(categorical_cols)} categorical columns...")
        
        encoding_method = self.config.get('categorical_encoding', 'onehot')
        
        for col in categorical_cols:
            if col == 'description' or len(self.data[col].unique()) > 50:
                # Skip high-cardinality text columns (handle with NLP instead)
                continue
            
            if encoding_method == 'target' and self.target:
                # Target encoding - requires target variable
                encoder = TargetEncoder()
                try:
                    if self.target in self.data.columns:
                        encoded = encoder.fit_transform(self.data[[col]], self.data[self.target])
                        self.data[f'{col}_encoded'] = encoded
                        self.encoders[col] = encoder
                        self.feature_log.append(f"Target encoded '{col}'")
                except:
                    # Fallback to label encoding
                    self._label_encode(col)
            
            elif encoding_method == 'onehot':
                # One-hot encoding for low cardinality
                if self.data[col].nunique() < 10:
                    dummies = pd.get_dummies(self.data[col], prefix=col, drop_first=True)
                    self.data = pd.concat([self.data, dummies], axis=1)
                    self.feature_log.append(f"One-hot encoded '{col}'")
                else:
                    self._label_encode(col)
            
            else:
                self._label_encode(col)
        
        logger.info(f"Encoded categorical features")
    
    def _label_encode(self, col: str):
        """Label encode a categorical column"""
        if col not in self.data.columns:
            return
        
        encoder = LabelEncoder()
        self.data[f'{col}_label'] = encoder.fit_transform(self.data[col].astype(str))
        self.encoders[col] = encoder
        self.feature_log.append(f"Label encoded '{col}'")
    
    def _identify_text_columns(self, categorical_cols: List[str]) -> List[str]:
        """Identify columns with text data suitable for NLP"""
        text_cols = []
        
        for col in categorical_cols:
            # Check if column contains text descriptions
            if col in ['description', 'notes', 'comments', 'text', 'content']:
                text_cols.append(col)
            elif self.data[col].dtype == 'object':
                # Check average string length
                avg_length = self.data[col].astype(str).str.len().mean()
                if avg_length > 30:  # Likely text data
                    text_cols.append(col)
        
        return text_cols
    
    def _vectorize_text(self, text_cols: List[str]):
        """Apply NLP vectorization to text columns"""
        logger.info(f"Vectorizing {len(text_cols)} text columns...")
        
        vectorization = self.config.get('text_vectorization', 'tfidf')
        
        for col in text_cols:
            if col not in self.data.columns:
                continue
            
            logger.info(f"Vectorizing '{col}' using {vectorization}...")
            
            try:
                if vectorization == 'tfidf':
                    vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
                else:
                    vectorizer = CountVectorizer(max_features=10, stop_words='english')
                
                # Convert column to string and vectorize
                text_data = self.data[col].astype(str).fillna("")
                vectors = vectorizer.fit_transform(text_data)
                
                # Convert sparse matrix to dense and create features
                feature_names = vectorizer.get_feature_names_out()
                for i, feature in enumerate(feature_names[:5]):  # Limit features
                    self.data[f'{col}_{feature}'] = vectors[:, i].toarray().flatten()
                
                self.text_vectorizers[col] = vectorizer
                self.feature_log.append(f"Vectorized text column '{col}' - {len(feature_names)} features")
                
            except Exception as e:
                logger.warning(f"Could not vectorize '{col}': {e}")
    
    def _create_interaction_features(self, numeric_cols: List[str]):
        """Create interaction features between top numeric columns"""
        logger.info("Creating interaction features...")
        
        # Create interactions for top 3 numeric features
        top_cols = numeric_cols[:min(3, len(numeric_cols))]
        
        for i in range(len(top_cols)):
            for j in range(i+1, len(top_cols)):
                col1, col2 = top_cols[i], top_cols[j]
                self.data[f'{col1}_x_{col2}'] = self.data[col1] * self.data[col2]
                self.feature_log.append(f"Created interaction: '{col1}' × '{col2}'")
        
        logger.info(f"Created interaction features")
    
    def _scale_numeric_features(self, numeric_cols: List[str]):
        """Scale numeric features to [0,1] range"""
        logger.info("Scaling numeric features...")
        
        scaler = StandardScaler()
        numeric_data = self.data[numeric_cols].copy()
        
        try:
            scaled = scaler.fit_transform(numeric_data)
            for i, col in enumerate(numeric_cols):
                self.data[f'{col}_scaled'] = scaled[:, i]
                self.feature_log.append(f"Scaled '{col}'")
        except Exception as e:
            logger.warning(f"Could not scale features: {e}")
    
    def get_engineered_data(self) -> pd.DataFrame:
        """Return feature-engineered data"""
        return self.data.copy()
    
    def get_feature_log(self) -> List[str]:
        """Return log of all features created"""
        return self.feature_log
    
    def get_feature_count(self) -> Dict:
        """Return count of original vs engineered features"""
        return {
            "original_features": self.original_data.shape[1],
            "engineered_features": self.data.shape[1],
            "features_created": self.data.shape[1] - self.original_data.shape[1],
            "engineering_actions": len(self.feature_log),
        }
    
    def print_feature_report(self):
        """Print detailed feature engineering report"""
        report = f"""
        FEATURE ENGINEERING REPORT
        ===========================
        Original Features: {self.original_data.shape[1]}
        Engineered Features: {self.data.shape[1]}
        New Features Created: {self.data.shape[1] - self.original_data.shape[1]}
        
        Actions Performed:
        {chr(10).join([f"  • {log}" for log in self.feature_log[:15]])}
        
        Final Data Shape: {self.data.shape[0]} rows × {self.data.shape[1]} columns
        """
        print(report)
        logger.info(report)
