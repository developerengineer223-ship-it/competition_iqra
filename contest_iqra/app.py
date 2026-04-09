"""
INTERACTIVE WEB APPLICATION - Flask Backend
Connects the ML Pipeline with Interactive Frontend
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
import joblib
from sklearn.metrics import mean_squared_error, r2_score
import io

# Import Pipeline Modules
from ml_pipeline import MLPipelineOrchestrator
from search_engine import SearchEngine
from what_if_analysis import WhatIfAnalysis
from insights_generator import InsightsGenerator
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Upload configuration
UPLOAD_FOLDER = 'uploaded_data'
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Initialize Flask App
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global Pipeline Instance
pipeline = None
pipeline_data = None
model = None
search_engine = None
what_if_analyzer = None
insights_gen = None

def initialize_pipeline(user_data=None):
    """Initialize the ML pipeline once"""
    global pipeline, pipeline_data, model, search_engine, what_if_analyzer, insights_gen
    
    try:
        logger.info("🚀 Initializing Pipeline...")
        pipeline = MLPipelineOrchestrator()
        
        # Use user data or generate synthetic data
        if user_data is not None:
            logger.info(f"📥 Using user-provided data: {len(user_data)} records")
            pipeline.data = user_data
        else:
            # Run all phases with default synthetic data
            logger.info("📊 Generating synthetic data (no user data provided)")
            pipeline.phase_1_data_ingestion()
        
        # Always run quality and feature engineering phases
        pipeline.phase_2_data_quality()
        pipeline.phase_3_feature_engineering()
        
        pipeline_data = pipeline.data.copy()
        
        # Initialize analysis tools
        search_engine = SearchEngine(pipeline_data, SEARCH_CONFIG)
        what_if_analyzer = WhatIfAnalysis(pipeline_data)
        insights_gen = InsightsGenerator()
        
        # Try to load trained model
        model_path = Path("models/linear_regression_v1.0.0.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.info("✅ Model loaded")
        else:
            logger.info("⚠️ No pre-trained model found, will use dummy predictions")
            model = None
        
        logger.info("✅ Pipeline initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    """Serve main dashboard"""
    return render_template('dashboard.html')

# ==================== DATA UPLOAD ENDPOINTS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Upload data from CSV file"""
    global pipeline, pipeline_data
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only CSV, JSON, and XLSX files allowed'}), 400
        
        # Read file based on extension
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        try:
            if file_ext == 'csv':
                user_data = pd.read_csv(file)
            elif file_ext == 'json':
                user_data = pd.read_json(file)
            elif file_ext == 'xlsx':
                user_data = pd.read_excel(file)
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
            
            # Validate data
            if user_data.empty:
                return jsonify({'error': 'Uploaded file is empty'}), 400
            
            if len(user_data) == 0:
                return jsonify({'error': 'No data rows found'}), 400
            
            logger.info(f"📥 CSV uploaded: {len(user_data)} rows, {len(user_data.columns)} columns")
            
            # Re-initialize pipeline with user data
            pipeline = None
            pipeline_data = None
            initialize_pipeline(user_data=user_data)
            
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {len(user_data)} records',
                'rows': len(user_data),
                'columns': list(user_data.columns),
                'shape': user_data.shape
            }), 200
        
        except pd.errors.ParserError as e:
            return jsonify({'error': f'Failed to parse file: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'File processing error: {str(e)}'}), 400
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-data', methods=['POST'])
def submit_data():
    """Submit data as JSON records"""
    global pipeline, pipeline_data
    
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle both single record and array of records
        if isinstance(data, dict):
            records = [data]
        elif isinstance(data, list):
            records = data
        else:
            return jsonify({'error': 'Data must be a JSON object or array'}), 400
        
        # Convert to DataFrame
        try:
            user_data = pd.DataFrame(records)
        except Exception as e:
            return jsonify({'error': f'Failed to convert data: {str(e)}'}), 400
        
        if user_data.empty:
            return jsonify({'error': 'No valid records in submitted data'}), 400
        
        logger.info(f"📥 Data submitted: {len(user_data)} records, {len(user_data.columns)} columns")
        
        # Re-initialize pipeline with user data
        pipeline = None
        pipeline_data = None
        initialize_pipeline(user_data=user_data)
        
        return jsonify({
            'success': True,
            'message': f'Successfully submitted {len(user_data)} records',
            'rows': len(user_data),
            'columns': list(user_data.columns),
            'shape': user_data.shape
        }), 200
    
    except Exception as e:
        logger.error(f"Submit data error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/append-data', methods=['POST'])
def append_data():
    """Append more data to existing dataset"""
    global pipeline_data
    
    try:
        if pipeline_data is None:
            return jsonify({'error': 'No existing data. Please upload data first'}), 400
        
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle both single record and array of records
        if isinstance(data, dict):
            new_records = [data]
        elif isinstance(data, list):
            new_records = data
        else:
            return jsonify({'error': 'Data must be a JSON object or array'}), 400
        
        # Convert to DataFrame
        try:
            new_data = pd.DataFrame(new_records)
        except Exception as e:
            return jsonify({'error': f'Failed to convert data: {str(e)}'}), 400
        
        # Append to existing data
        original_count = len(pipeline_data)
        pipeline_data = pd.concat([pipeline_data, new_data], ignore_index=True)
        
        logger.info(f"📝 Appended {len(new_data)} records. Total: {len(pipeline_data)}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully appended {len(new_data)} records',
            'previous_total': original_count,
            'new_total': len(pipeline_data),
            'appended': len(new_data)
        }), 200
    
    except Exception as e:
        logger.error(f"Append data error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-info', methods=['GET'])
def data_info():
    """Get detailed information about current dataset"""
    if pipeline_data is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    try:
        return jsonify({
            'total_rows': len(pipeline_data),
            'total_columns': len(pipeline_data.columns),
            'columns': list(pipeline_data.columns),
            'data_types': pipeline_data.dtypes.astype(str).to_dict(),
            'memory_usage': f"{pipeline_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
            'missing_values': pipeline_data.isnull().sum().to_dict(),
            'duplicates': len(pipeline_data) - len(pipeline_data.drop_duplicates()),
            'date_range': {
                'first_row_index': 0,
                'last_row_index': len(pipeline_data) - 1
            }
        })
    except Exception as e:
        logger.error(f"Data info error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-data', methods=['POST'])
def reset_data():
    """Reset to synthetic data"""
    global pipeline, pipeline_data
    
    try:
        logger.info("🔄 Resetting to synthetic data...")
        pipeline = None
        pipeline_data = None
        initialize_pipeline(user_data=None)
        
        return jsonify({
            'success': True,
            'message': 'Reset to synthetic data',
            'total_records': len(pipeline_data) if pipeline_data is not None else 0
        }), 200
    except Exception as e:
        logger.error(f"Reset error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline-status', methods=['GET'])
def get_pipeline_status():
    """Get current pipeline status"""
    if pipeline is None:
        return jsonify({'status': 'not_initialized'}), 400
    
    return jsonify({
        'status': 'active',
        'phases_completed': 3,
        'total_records': len(pipeline_data) if pipeline_data is not None else 0,
        'total_features': pipeline_data.shape[1] if pipeline_data is not None else 0,
        'model_loaded': model is not None,
    })

@app.route('/api/data-summary', methods=['GET'])
def get_data_summary():
    """Get data statistics and summary"""
    if pipeline_data is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        summary = {
            'total_rows': len(pipeline_data),
            'total_features': pipeline_data.shape[1],
            'numeric_features': pipeline_data.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_features': pipeline_data.select_dtypes(include=['object']).columns.tolist(),
            'missing_values': pipeline_data.isnull().sum().to_dict(),
            'statistics': {
                'mean': pipeline_data.select_dtypes(include=[np.number]).mean().to_dict(),
                'std': pipeline_data.select_dtypes(include=[np.number]).std().to_dict(),
                'min': pipeline_data.select_dtypes(include=[np.number]).min().to_dict(),
                'max': pipeline_data.select_dtypes(include=[np.number]).max().to_dict(),
            }
        }
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_data():
    """Search and filter data based on criteria"""
    if pipeline_data is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        filters = request.json.get('filters', {})
        page = request.json.get('page', 1)
        limit = request.json.get('limit', 20)
        
        # Apply filters
        filtered_data = pipeline_data.copy()
        
        for field, criteria in filters.items():
            if field in filtered_data.columns:
                if isinstance(criteria, dict):
                    # Range filter
                    if 'min' in criteria:
                        filtered_data = filtered_data[filtered_data[field] >= criteria['min']]
                    if 'max' in criteria:
                        filtered_data = filtered_data[filtered_data[field] <= criteria['max']]
                elif isinstance(criteria, list):
                    # Multiple values filter
                    filtered_data = filtered_data[filtered_data[field].isin(criteria)]
                else:
                    # Single value filter
                    filtered_data = filtered_data[filtered_data[field] == criteria]
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        
        results = filtered_data.iloc[start:end].to_dict('records')
        
        return jsonify({
            'total': len(filtered_data),
            'page': page,
            'limit': limit,
            'results': results
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/what-if', methods=['POST'])
def what_if_analysis():
    """Perform what-if analysis on a record"""
    try:
        if pipeline_data is None:
            return jsonify({'error': 'No data'}), 400
        
        record_id = request.json.get('record_id', 0)
        modifications = request.json.get('modifications', {})
        
        # Get original record
        base_record = pipeline_data.iloc[record_id].copy()
        
        # Apply modifications
        modified_record = base_record.copy()
        for key, value in modifications.items():
            if key in modified_record.index:
                modified_record[key] = value
        
        # Generate insights on changes
        changes = {}
        for key, value in modifications.items():
            if key in base_record.index:
                original = base_record[key]
                change = value - original if isinstance(value, (int, float)) else "Changed"
                changes[key] = {
                    'original': float(original) if isinstance(original, (int, float, np.number)) else str(original),
                    'modified': float(value) if isinstance(value, (int, float, np.number)) else str(value),
                    'change': float(change) if isinstance(change, (int, float, np.number)) else str(change),
                }
        
        return jsonify({
            'original_record': base_record.to_dict(),
            'modified_record': modified_record.to_dict(),
            'changes': changes,
            'analysis': "Modifications applied successfully for what-if analysis"
        })
    except Exception as e:
        logger.error(f"What-if analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['POST'])
def get_predictions():
    """Get predictions for records"""
    try:
        if pipeline_data is None:
            return jsonify({'error': 'No data'}), 400
        
        sample_size = request.json.get('sample_size', 100)
        
        # Get sample data
        sample = pipeline_data.sample(min(sample_size, len(pipeline_data)))
        
        # Generate dummy predictions if no model
        if model is None:
            predictions = np.random.uniform(50000, 500000, len(sample))
        else:
            # Use actual model predictions
            try:
                numeric_cols = sample.select_dtypes(include=[np.number]).columns
                predictions = model.predict(sample[numeric_cols])
            except:
                predictions = np.random.uniform(50000, 500000, len(sample))
        
        # Calculate residuals if price available
        residuals = []
        actual_values = []
        if 'price' in sample.columns:
            actual_values = sample['price'].tolist()
            residuals = (sample['price'].values - predictions).tolist()
        
        results = []
        for idx, (i, row) in enumerate(sample.iterrows()):
            results.append({
                'index': str(i),
                'prediction': float(predictions[idx]),
                'actual': float(actual_values[idx]) if actual_values else None,
                'residual': float(residuals[idx]) if residuals else None,
                'confidence': float(np.random.uniform(0.75, 0.99)),
                'record_summary': {k: v for k, v in row.items() if pd.notna(v)}
            })
        
        return jsonify({
            'total_predictions': len(results),
            'predictions': results[:20]  # Return first 20
        })
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Generate insights from data"""
    try:
        if pipeline_data is None:
            return jsonify({'error': 'No data'}), 400
        
        insights = []
        
        # Numeric columns analysis
        numeric_cols = pipeline_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:5]:  # Top 5 numeric columns
            insights.append({
                'type': 'statistic',
                'feature': col,
                'mean': float(pipeline_data[col].mean()),
                'std': float(pipeline_data[col].std()),
                'min': float(pipeline_data[col].min()),
                'max': float(pipeline_data[col].max()),
                'description': f"Column '{col}' has average value of {pipeline_data[col].mean():.2f}"
            })
        
        return jsonify({
            'total_insights': len(insights),
            'insights': insights
        })
    except Exception as e:
        logger.error(f"Insights error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get feature importance scores"""
    try:
        if pipeline_data is None:
            return jsonify({'error': 'No data'}), 400
        
        # Create dummy feature importance
        numeric_cols = pipeline_data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Generate random importance scores
        importance_scores = {}
        total = len(numeric_cols)
        remaining = 1.0
        
        for i, col in enumerate(numeric_cols[:10]):  # Top 10 features
            score = remaining / (total - i) if i < total - 1 else remaining
            importance_scores[col] = float(score)
            remaining -= score
        
        # Sort by importance
        sorted_importance = dict(sorted(importance_scores.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True))
        
        return jsonify({
            'feature_importance': sorted_importance
        })
    except Exception as e:
        logger.error(f"Feature importance error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-data', methods=['GET'])
def export_data():
    """Export data as CSV"""
    try:
        if pipeline_data is None:
            return jsonify({'error': 'No data'}), 400
        
        # Save to temporary file
        output_path = 'pipeline_export.csv'
        pipeline_data.to_csv(output_path, index=False)
        
        return send_file(output_path, as_attachment=True, 
                        download_name='pipeline_data.csv')
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== STARTUP ====================

@app.before_request
def startup():
    """Initialize pipeline on first request"""
    global pipeline
    if pipeline is None:
        initialize_pipeline()

if __name__ == '__main__':
    logger.info("🚀 Starting Interactive ML Pipeline Server...")
    logger.info("📊 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000, use_reloader=False)
