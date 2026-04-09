"""
PHASE 4: Search Engine Module
Dynamic search and filtering of prediction results by key variables
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Dynamic search engine for filtering prediction results
    Supports filtering by multiple criteria, range queries, and full-text search
    """
    
    def __init__(self, predictions_df: pd.DataFrame, config: Dict = None):
        self.predictions = predictions_df.copy()
        self.config = config or {}
        self.search_history = []
        self.indexes = {}
        self._build_indexes()
        logger.info(f"SearchEngine initialized with {len(predictions_df)} records")
    
    def _build_indexes(self):
        """Build indexes on categorical and numeric columns for faster search"""
        for col in self.predictions.columns:
            if self.predictions[col].dtype == 'object':
                # Index categorical columns
                self.indexes[col] = self.predictions[col].unique().tolist()
            elif self.predictions[col].dtype in ['int64', 'float64']:
                # Store min/max for numeric columns
                self.indexes[col] = {
                    'min': self.predictions[col].min(),
                    'max': self.predictions[col].max()
                }
        
        logger.info(f"Built indexes for {len(self.indexes)} columns")
    
    def search_by_field(self, field: str, value: Any, operator: str = '==') -> pd.DataFrame:
        """
        Search for records by field value
        Operators: '==', '!=', '>', '<', '>=', '<=', 'in', 'contains'
        """
        logger.info(f"Searching: {field} {operator} {value}")
        
        if field not in self.predictions.columns:
            logger.warning(f"Field '{field}' not found")
            return pd.DataFrame()
        
        try:
            if operator == '==':
                result = self.predictions[self.predictions[field] == value]
            elif operator == '!=':
                result = self.predictions[self.predictions[field] != value]
            elif operator == '>':
                result = self.predictions[self.predictions[field] > value]
            elif operator == '<':
                result = self.predictions[self.predictions[field] < value]
            elif operator == '>=':
                result = self.predictions[self.predictions[field] >= value]
            elif operator == '<=':
                result = self.predictions[self.predictions[field] <= value]
            elif operator == 'in':
                result = self.predictions[self.predictions[field].isin(value)]
            elif operator == 'contains':
                result = self.predictions[self.predictions[field].astype(str).str.contains(str(value), case=False, na=False)]
            else:
                logger.warning(f"Unknown operator: {operator}")
                return pd.DataFrame()
            
            self.search_history.append({
                'query': f"{field} {operator} {value}",
                'results': len(result),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Found {len(result)} matching records")
            return result
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return pd.DataFrame()
    
    def range_search(self, field: str, min_val: float, max_val: float) -> pd.DataFrame:
        """Search for records within a numeric range"""
        logger.info(f"Range search: {field} between {min_val} and {max_val}")
        
        result = self.predictions[
            (self.predictions[field] >= min_val) & 
            (self.predictions[field] <= max_val)
        ]
        
        self.search_history.append({
            'query': f"{field} in [{min_val}, {max_val}]",
            'results': len(result),
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def multi_filter(self, filters: Dict[str, Tuple[str, Any]]) -> pd.DataFrame:
        """
        Apply multiple filters at once
        filters: {field: (operator, value), ...}
        """
        logger.info(f"Applying {len(filters)} filters...")
        
        result = self.predictions.copy()
        applied_filters = []
        
        for field, (operator, value) in filters.items():
            if field not in self.predictions.columns:
                logger.warning(f"Field '{field}' not found")
                continue
            
            try:
                if operator == '==':
                    result = result[result[field] == value]
                elif operator == '>':
                    result = result[result[field] > value]
                elif operator == '<':
                    result = result[result[field] < value]
                elif operator == 'in':
                    result = result[result[field].isin(value)]
                elif operator == 'contains':
                    result = result[result[field].astype(str).str.contains(str(value), case=False)]
                
                applied_filters.append(f"{field} {operator} {value}")
            
            except Exception as e:
                logger.warning(f"Filter error on '{field}': {e}")
        
        self.search_history.append({
            'query': ' AND '.join(applied_filters),
            'results': len(result),
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Multi-filter returned {len(result)} records")
        return result
    
    def sort_by(self, field: str, ascending: bool = True) -> pd.DataFrame:
        """Sort results by field"""
        logger.info(f"Sorting by {field} ({'ascending' if ascending else 'descending'})")
        return self.predictions.sort_values(field, ascending=ascending)
    
    def paginate(self, page: int = 1, page_size: int = 100) -> Tuple[pd.DataFrame, Dict]:
        """Paginate results"""
        total_records = len(self.predictions)
        total_pages = (total_records + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_data = self.predictions.iloc[start_idx:end_idx]
        
        pagination_info = {
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_records': total_records,
            'records_in_page': len(page_data),
        }
        
        return page_data, pagination_info
    
    def get_unique_values(self, field: str, limit: int = 50) -> List[Any]:
        """Get unique values for a field"""
        if field not in self.predictions.columns:
            return []
        
        unique = self.predictions[field].unique().tolist()
        return unique[:limit]
    
    def get_statistics(self, field: str) -> Dict:
        """Get statistics for a numeric field"""
        if field not in self.predictions.columns:
            return {}
        
        if self.predictions[field].dtype not in ['int64', 'float64']:
            return {'type': 'categorical', 'unique_values': self.predictions[field].nunique()}
        
        return {
            'field': field,
            'type': 'numeric',
            'min': float(self.predictions[field].min()),
            'max': float(self.predictions[field].max()),
            'mean': float(self.predictions[field].mean()),
            'median': float(self.predictions[field].median()),
            'std': float(self.predictions[field].std()),
            'count': int(self.predictions[field].count()),
        }
    
    def search_history_report(self) -> pd.DataFrame:
        """Get report of search history"""
        if not self.search_history:
            return pd.DataFrame()
        return pd.DataFrame(self.search_history)
    
    def export_search_results(self, results: pd.DataFrame, format: str = 'csv') -> str:
        """Export search results to file"""
        filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        try:
            if format == 'csv':
                results.to_csv(filename, index=False)
            elif format == 'json':
                results.to_json(filename, orient='records')
            elif format == 'parquet':
                results.to_parquet(filename)
            
            logger.info(f"Exported {len(results)} records to {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Export error: {e}")
            return ""
    
    def create_filter_widget_config(self) -> Dict:
        """Create configuration for UI filter widget"""
        config = {
            'fields': [],
            'filters': {}
        }
        
        for col in self.predictions.columns:
            if self.predictions[col].dtype == 'object':
                config['fields'].append({
                    'name': col,
                    'type': 'categorical',
                    'values': self.get_unique_values(col)
                })
            elif self.predictions[col].dtype in ['int64', 'float64']:
                stats = self.get_statistics(col)
                config['fields'].append({
                    'name': col,
                    'type': 'numeric',
                    'min': stats['min'],
                    'max': stats['max'],
                })
        
        return config
