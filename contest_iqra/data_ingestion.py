"""
PHASE 1: Data Ingestion Module
Handles data loading, connection to various sources, and AI Catalog registration
"""

import pandas as pd
import numpy as np
import logging
from typing import Union, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DataIngestion:
    """
    Connects to various data sources and registers datasets in AI Catalog
    Supports: CSV, Parquet, SQL, Snowflake, and synthetic data generation
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.data = None
        self.metadata = {
            "source": None,
            "rows": 0,
            "columns": 0,
            "data_types": {},
            "catalog_entry": None,
        }
        logger.info("DataIngestion initialized")
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            self.data = pd.read_csv(filepath)
            self.metadata["source"] = f"csv://{filepath}"
            self._update_metadata()
            logger.info(f"Loaded CSV from {filepath}: {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_parquet(self, filepath: str) -> pd.DataFrame:
        """Load data from Parquet file"""
        try:
            self.data = pd.read_parquet(filepath)
            self.metadata["source"] = f"parquet://{filepath}"
            self._update_metadata()
            logger.info(f"Loaded Parquet from {filepath}: {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading Parquet: {e}")
            raise
    
    def load_from_snowflake(self, connection_params: Dict, query: str) -> pd.DataFrame:
        """
        Load data from Snowflake (mock implementation)
        In production, use snowflake-sqlalchemy or snowflake-connector-python
        """
        logger.info(f"Loading from Snowflake: {connection_params.get('database')}")
        # This is a mock - in production, use actual Snowflake SDK
        logger.warning("Using mock Snowflake connection - configure real connection in production")
        return self._generate_synthetic_data()
    
    def load_from_database(self, connection_string: str, query: str) -> pd.DataFrame:
        """
        Load data from SQL database
        Supports: PostgreSQL, MySQL, Oracle, MSSQL
        """
        logger.info(f"Loading from database: {connection_string[:30]}...")
        # In production: from sqlalchemy import create_engine
        # engine = create_engine(connection_string)
        # self.data = pd.read_sql(query, engine)
        return self._generate_synthetic_data()
    
    def _generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate realistic synthetic data for demonstration"""
        np.random.seed(42)
        
        self.data = pd.DataFrame({
            'id': range(1, n_samples + 1),
            'price': np.random.uniform(50000, 500000, n_samples),
            'square_feet': np.random.uniform(800, 5000, n_samples),
            'bedrooms': np.random.randint(1, 6, n_samples),
            'bathrooms': np.random.uniform(1, 4, n_samples),
            'age_years': np.random.randint(0, 100, n_samples),
            'garage_spaces': np.random.randint(0, 4, n_samples),
            'pool': np.random.choice([0, 1], n_samples),
            'neighborhood': np.random.choice(['Downtown', 'Suburbs', 'Rural'], n_samples),
            'condition': np.random.choice(['Poor', 'Fair', 'Good', 'Excellent'], n_samples),
            'description': [f'Property in location {i}' for i in range(n_samples)],
        })
        
        # Add some missing values realistically
        missing_indices = np.random.choice(n_samples, size=int(0.05*n_samples), replace=False)
        self.data.loc[missing_indices, 'garage_spaces'] = np.nan
        
        missing_indices = np.random.choice(n_samples, size=int(0.03*n_samples), replace=False)
        self.data.loc[missing_indices, 'age_years'] = np.nan
        
        self.metadata["source"] = "synthetic_data"
        self._update_metadata()
        logger.info(f"Generated synthetic data: {self.data.shape}")
        
        return self.data
    
    def register_in_catalog(self, dataset_name: str, description: str = "") -> Dict:
        """Register dataset in AI Catalog"""
        catalog_entry = {
            "name": dataset_name,
            "description": description or f"Dataset {dataset_name}",
            "source": self.metadata["source"],
            "rows": self.metadata["rows"],
            "columns": self.metadata["columns"],
            "columns_list": list(self.data.columns),
            "data_types": self.metadata["data_types"],
            "registration_timestamp": pd.Timestamp.now().isoformat(),
            "status": "registered",
        }
        
        self.metadata["catalog_entry"] = catalog_entry
        logger.info(f"Registered dataset '{dataset_name}' in AI Catalog")
        return catalog_entry
    
    def _update_metadata(self):
        """Update internal metadata"""
        if self.data is not None:
            self.metadata["rows"] = self.data.shape[0]
            self.metadata["columns"] = self.data.shape[1]
            self.metadata["data_types"] = self.data.dtypes.to_dict()
    
    def get_data(self) -> pd.DataFrame:
        """Return loaded data"""
        return self.data.copy()
    
    def get_metadata(self) -> Dict:
        """Return metadata about the dataset"""
        return self.metadata
    
    def get_column_stats(self) -> Dict:
        """Get basic statistics about columns"""
        stats = {
            "numeric_columns": self.data.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": self.data.select_dtypes(include=['object']).columns.tolist(),
            "column_count": self.data.shape[1],
            "row_count": self.data.shape[0],
        }
        return stats
