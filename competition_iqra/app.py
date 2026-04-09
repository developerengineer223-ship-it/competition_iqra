from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)

# File upload configuration
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# 1. DATA SANITIZER - Pandas Cleaning Function
# ============================================
def sanitize_data(df):
    """
    Automatically handles missing values, removes duplicates, 
    and converts/replaces string data
    """
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    for col in df.columns:
        if df[col].dtype == 'object':
            # For string columns: fill with 'Unknown'
            df[col] = df[col].fillna('Unknown')
        elif pd.api.types.is_numeric_dtype(df[col]):
            # For numeric columns: fill with mean
            df[col] = df[col].fillna(df[col].mean())
        else:
            # For other types: fill with 'Unknown'
            df[col] = df[col].fillna('Unknown')
    
    # Convert data types appropriately
    for col in df.columns:
        if col.lower() in ['date', 'created_at', 'updated_at', 'purchase_date']:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
        elif df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
    
    return df

# ============================================
# 2. DYNAMIC FILTERING FUNCTION
# ============================================
def dynamic_filter(df, tool_type, filters):
    """
    Filter data based on tool type:
    - Sales Tool: filter by Category and Date Range
    - Health Tool: filter by Age Group and Condition
    """
    filtered_df = df.copy()
    
    if tool_type == "sales":
        # Filter by Category
        if 'category' in filters and filters['category']:
            filtered_df = filtered_df[filtered_df['Category'] == filters['category']]
        
        # Filter by Date Range
        if 'start_date' in filters and filters['start_date']:
            start_date = pd.to_datetime(filters['start_date'])
            filtered_df = filtered_df[filtered_df['Date'] >= start_date]
        
        if 'end_date' in filters and filters['end_date']:
            end_date = pd.to_datetime(filters['end_date'])
            filtered_df = filtered_df[filtered_df['Date'] <= end_date]
    
    elif tool_type == "health":
        # Filter by Age Group
        if 'age_group' in filters and filters['age_group']:
            age_group = filters['age_group']
            if age_group == "0-18":
                filtered_df = filtered_df[(filtered_df['Age'] >= 0) & (filtered_df['Age'] <= 18)]
            elif age_group == "19-35":
                filtered_df = filtered_df[(filtered_df['Age'] >= 19) & (filtered_df['Age'] <= 35)]
            elif age_group == "36-60":
                filtered_df = filtered_df[(filtered_df['Age'] >= 36) & (filtered_df['Age'] <= 60)]
            elif age_group == "60+":
                filtered_df = filtered_df[filtered_df['Age'] > 60]
        
        # Filter by Condition
        if 'condition' in filters and filters['condition']:
            filtered_df = filtered_df[filtered_df['Condition'] == filters['condition']]
    
    return filtered_df

# ============================================
# 3. AI LOGIC - RECOMMENDATION ENGINE
# ============================================
def get_recommendations(df, tool_type):
    """
    AI logic to suggest actions based on processed data
    """
    recommendations = []
    
    if tool_type == "sales" and len(df) > 0:
        # Sales recommendations
        top_category = df['Category'].value_counts().index[0]
        avg_sales = df['Sales'].mean()
        total_sales = df['Sales'].sum()
        
        recommendations.append({
            'title': f'Top Selling Category: {top_category}',
            'description': f'Focus on {top_category} - it accounts for {(df[df["Category"]==top_category].shape[0]/len(df)*100):.1f}% of sales',
            'action': f'Increase inventory for {top_category}'
        })
        
        if avg_sales > 5000:
            recommendations.append({
                'title': 'High Revenue Period',
                'description': f'Average sale value is ${avg_sales:.2f} - excellent performance!',
                'action': 'Maintain current pricing strategy'
            })
        
        if total_sales > 300000:
            recommendations.append({
                'title': 'Strong Sales Volume',
                'description': f'Total sales: ${total_sales:,.2f} - Consider expanding product lines',
                'action': 'Introduce premium products'
            })
    
    elif tool_type == "health" and len(df) > 0:
        # Health recommendations
        avg_cholesterol = df['Cholesterol'].mean() if 'Cholesterol' in df.columns else 0
        condition_counts = df['Condition'].value_counts()
        
        most_common_condition = condition_counts.index[0]
        recommendations.append({
            'title': f'Most Common Condition: {most_common_condition}',
            'description': f'{most_common_condition} affects {(condition_counts.iloc[0]/len(df)*100):.1f}% of patients',
            'action': f'Allocate resources for {most_common_condition} treatment'
        })
        
        if avg_cholesterol > 200:
            recommendations.append({
                'title': 'High Cholesterol Alert',
                'description': f'Average cholesterol level: {avg_cholesterol:.1f} mg/dL - above recommended',
                'action': 'Recommend dietary adjustments and regular monitoring'
            })
        
        young_patients = df[df['Age'] < 30].shape[0]
        if young_patients > 0:
            recommendations.append({
                'title': 'Young Patient Population',
                'description': f'{young_patients} patients under 30 years old',
                'action': 'Implement preventive care programs for younger demographics'
            })
    
    return recommendations

# ============================================
# 3B. HEALTH CONDITION ANALYZER - User Input
# ============================================
def analyze_health_condition(age, cholesterol, blood_pressure, symptoms=[]):
    """
    Analyze individual health condition based on user input
    Returns diagnosis, risk level, and recommendations
    """
    diagnosis = {
        'age': age,
        'cholesterol': cholesterol,
        'blood_pressure': blood_pressure,
        'risk_level': 'Low',
        'predicted_condition': 'Normal',
        'analysis': [],
        'recommendations': [],
        'warning_signs': []
    }
    
    # Parse blood pressure (expect "Systolic/Diastolic")
    bp_list = blood_pressure.split('/') if isinstance(blood_pressure, str) else [blood_pressure, 80]
    systolic = int(bp_list[0]) if len(bp_list) > 0 else blood_pressure
    diastolic = int(bp_list[1]) if len(bp_list) > 1 else 80
    
    risk_score = 0
    
    # Age analysis
    if age < 18:
        diagnosis['analysis'].append("You are under 18 years old - focus on healthy lifestyle habits")
    elif age > 60:
        diagnosis['analysis'].append(f"Age {age}: Requires regular health monitoring and preventive care")
        risk_score += 2
    
    # Cholesterol analysis
    if cholesterol < 200:
        diagnosis['analysis'].append(f"Cholesterol {cholesterol} mg/dL: Healthy level ✓")
    elif cholesterol < 240:
        diagnosis['analysis'].append(f"Cholesterol {cholesterol} mg/dL: Borderline high")
        risk_score += 1
        diagnosis['warning_signs'].append("High cholesterol detected")
    else:
        diagnosis['analysis'].append(f"Cholesterol {cholesterol} mg/dL: High - requires attention")
        risk_score += 2
        diagnosis['warning_signs'].append("Very high cholesterol - seek medical advice")
    
    # Blood Pressure analysis
    if systolic < 120 and diastolic < 80:
        diagnosis['analysis'].append(f"BP {systolic}/{diastolic}: Normal ✓")
    elif systolic < 130 and diastolic < 80:
        diagnosis['analysis'].append(f"BP {systolic}/{diastolic}: Elevated - monitor regularly")
        risk_score += 1
    elif systolic < 140 or diastolic < 90:
        diagnosis['analysis'].append(f"BP {systolic}/{diastolic}: Stage 1 Hypertension")
        risk_score += 2
        diagnosis['warning_signs'].append("Hypertension detected")
    else:
        diagnosis['analysis'].append(f"BP {systolic}/{diastolic}: Stage 2 Hypertension - seek medical care")
        risk_score += 3
        diagnosis['warning_signs'].append("Severe hypertension - urgent medical attention needed")
    
    # Determine risk level
    if risk_score == 0:
        diagnosis['risk_level'] = 'Low'
        diagnosis['predicted_condition'] = 'Normal - Healthy'
    elif risk_score <= 2:
        diagnosis['risk_level'] = 'Moderate'
        diagnosis['predicted_condition'] = 'At Risk'
    elif risk_score <= 4:
        diagnosis['risk_level'] = 'High'
        diagnosis['predicted_condition'] = 'Heart Disease Risk'
    else:
        diagnosis['risk_level'] = 'Critical'
        diagnosis['predicted_condition'] = 'Requires Immediate Medical Attention'
    
    # Generate recommendations
    if cholesterol >= 200:
        diagnosis['recommendations'].append({
            'action': 'Dietary Changes',
            'detail': 'Reduce saturated fats, increase fiber intake, eat more leafy greens'
        })
        diagnosis['recommendations'].append({
            'action': 'Exercise',
            'detail': '30 minutes of cardio 5 days per week to lower cholesterol'
        })
    
    if systolic >= 130 or diastolic >= 80:
        diagnosis['recommendations'].append({
            'action': 'Reduce Sodium',
            'detail': 'Limit salt intake to less than 2,300mg per day'
        })
        diagnosis['recommendations'].append({
            'action': 'Regular Monitoring',
            'detail': 'Check blood pressure daily and maintain a log'
        })
    
    if age > 50:
        diagnosis['recommendations'].append({
            'action': 'Annual Health Checkup',
            'detail': 'Get comprehensive health screening annually'
        })
    
    if risk_score == 0:
        diagnosis['recommendations'].append({
            'action': 'Maintain Healthy Lifestyle',
            'detail': 'Keep up with regular exercise, healthy diet, and sleep 7-9 hours daily'
        })
    
    return diagnosis

# ============================================
# 4. STATISTICAL SUMMARY FUNCTION
# ============================================
def get_statistics(df, tool_type):
    """
    Generate quick stats for dashboard
    """
    stats = {
        'total_records': len(df),
        'columns': len(df.columns),
    }
    
    if tool_type == "sales":
        if 'Sales' in df.columns:
            stats['total_sales'] = f"${df['Sales'].sum():,.2f}"
            stats['avg_sales'] = f"${df['Sales'].mean():,.2f}"
            stats['max_sales'] = f"${df['Sales'].max():,.2f}"
            stats['min_sales'] = f"${df['Sales'].min():,.2f}"
        if 'Category' in df.columns:
            stats['categories'] = df['Category'].nunique()
            stats['top_category'] = df['Category'].value_counts().index[0]
    
    elif tool_type == "health":
        stats['total_patients'] = len(df)
        if 'Age' in df.columns:
            stats['avg_age'] = f"{df['Age'].mean():.1f}"
            stats['age_range'] = f"{df['Age'].min():.0f} - {df['Age'].max():.0f}"
        if 'Condition' in df.columns:
            stats['conditions'] = df['Condition'].nunique()
            stats['common_condition'] = df['Condition'].value_counts().index[0]
        if 'Cholesterol' in df.columns:
            stats['avg_cholesterol'] = f"{df['Cholesterol'].mean():.1f}"
    
    return stats

# ============================================
# SAMPLE DATA GENERATION
# ============================================
def generate_sales_data():
    """Generate sample sales dataset"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200)
    data = {
        'Date': dates,
        'Category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Home'], 200),
        'Sales': np.random.randint(500, 10000, 200),
        'Quantity': np.random.randint(1, 50, 200),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 200)
    }
    return pd.DataFrame(data)

def generate_health_data():
    """Generate sample health dataset"""
    np.random.seed(42)
    data = {
        'Age': np.random.randint(18, 80, 150),
        'Cholesterol': np.random.randint(150, 300, 150),
        'BloodPressure': np.random.choice(['Normal', 'Pre-High', 'High'], 150),
        'Condition': np.random.choice(['Diabetes', 'Heart Disease', 'Hypertension', 'Normal'], 150),
        'Gender': np.random.choice(['Male', 'Female'], 150)
    }
    return pd.DataFrame(data)

# Global data storage
data_store = {
    'sales': sanitize_data(generate_sales_data()),
    'health': sanitize_data(generate_health_data())
}

# ============================================
# 5. FILE EXPORT CAPABILITY
# ============================================
def export_to_csv(df, filename):
    """Export dataframe to CSV"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

def export_to_excel(df, filename):
    """Export dataframe to Excel"""
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    return excel_buffer

# ============================================
# 6. SEARCH FUNCTIONALITY
# ============================================
def search_data(df, search_term, columns=None):
    """
    Search through dataframe for matching records
    """
    if columns is None:
        columns = df.columns
    
    mask = pd.Series([False] * len(df))
    search_term = str(search_term).lower()
    
    for col in columns:
        if col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(search_term)
    
    return df[mask]

# ============================================
# 7. INTERACTIVE VISUALIZATIONS
# ============================================
def create_sales_chart(df, chart_type='bar'):
    """Create interactive sales visualizations"""
    if len(df) == 0:
        return None
    
    try:
        if chart_type == 'bar':
            sales_by_cat = df.groupby('Category')['Sales'].sum().reset_index()
            fig = px.bar(sales_by_cat,
                        x='Category', y='Sales',
                        title='Sales by Category',
                        labels={'Sales': 'Total Sales ($)', 'Category': 'Product Category'},
                        color='Sales',
                        color_continuous_scale='Viridis')
        elif chart_type == 'line':
            daily_sales = df.groupby(df['Date'].dt.date)['Sales'].sum().reset_index()
            daily_sales.columns = ['Date', 'Sales']
            fig = px.line(daily_sales, x='Date', y='Sales',
                         title='Daily Sales Trend',
                         labels={'Sales': 'Daily Sales ($)'},
                         markers=True)
        elif chart_type == 'pie':
            sales_by_cat = df.groupby('Category')['Sales'].sum().reset_index()
            fig = px.pie(sales_by_cat, names='Category', values='Sales',
                        title='Sales Distribution by Category')
        
        fig.update_layout(height=500, showlegend=True, hovermode='closest')
        return fig.to_json()
    except Exception as e:
        print(f"Chart error: {str(e)}")
        return None

def create_health_chart(df, chart_type='bar'):
    """Create interactive health visualizations"""
    if len(df) == 0:
        return None
    
    try:
        if chart_type == 'bar':
            condition_counts = df['Condition'].value_counts().reset_index()
            condition_counts.columns = ['Condition', 'count']
            fig = px.bar(condition_counts,
                        x='Condition', y='count',
                        title='Patient Distribution by Condition',
                        labels={'count': 'Number of Patients', 'Condition': 'Medical Condition'},
                        color='count',
                        color_continuous_scale='Blues')
        elif chart_type == 'line':
            # Create age groups
            age_bins = [0, 18, 35, 60, 100]
            age_labels = ['0-18', '19-35', '36-60', '60+']
            df_copy = df.copy()
            df_copy['AgeGroup'] = pd.cut(df_copy['Age'], bins=age_bins, labels=age_labels)
            age_counts = df_copy['AgeGroup'].value_counts().sort_index().reset_index()
            age_counts.columns = ['AgeGroup', 'count']
            fig = px.line(age_counts, x='AgeGroup', y='count',
                         title='Age Group Distribution',
                         labels={'count': 'Number of Patients', 'AgeGroup': 'Age Group'},
                         markers=True)
        elif chart_type == 'pie':
            condition_counts = df['Condition'].value_counts().reset_index()
            condition_counts.columns = ['Condition', 'count']
            fig = px.pie(condition_counts, names='Condition', values='count',
                        title='Patient Distribution by Condition')
        
        fig.update_layout(height=500, showlegend=True, hovermode='closest')
        return fig.to_json()
    except Exception as e:
        print(f"Chart error: {str(e)}")
        return None

# ============================================
# FLASK ROUTES
# ============================================
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('tamplates.html')

@app.route('/api/tool_select', methods=['POST'])
def select_tool():
    """Select between Sales or Health tool"""
    tool_type = request.json.get('tool_type')
    
    if tool_type not in ['sales', 'health']:
        return jsonify({'error': 'Invalid tool type'}), 400
    
    df = data_store[tool_type]
    stats = get_statistics(df, tool_type)
    
    return jsonify({
        'tool_type': tool_type,
        'stats': stats,
        'data_preview': df.head(10).to_dict(orient='records')
    })

@app.route('/api/filter', methods=['POST'])
def apply_filter():
    """Apply dynamic filters"""
    tool_type = request.json.get('tool_type')
    filters = request.json.get('filters', {})
    
    df = data_store[tool_type]
    filtered_df = dynamic_filter(df, tool_type, filters)
    
    stats = get_statistics(filtered_df, tool_type)
    recommendations = get_recommendations(filtered_df, tool_type)
    
    return jsonify({
        'stats': stats,
        'recommendations': recommendations,
        'data_preview': filtered_df.head(10).to_dict(orient='records'),
        'record_count': len(filtered_df)
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Search functionality"""
    tool_type = request.json.get('tool_type')
    search_term = request.json.get('search_term')
    
    df = data_store[tool_type]
    results = search_data(df, search_term)
    
    return jsonify({
        'results': results.to_dict(orient='records'),
        'count': len(results)
    })

@app.route('/api/chart', methods=['POST'])
def get_chart():
    """Generate interactive charts"""
    tool_type = request.json.get('tool_type')
    chart_type = request.json.get('chart_type', 'bar')
    
    df = data_store[tool_type]
    
    if tool_type == 'sales':
        chart_html = create_sales_chart(df, chart_type)
    else:
        chart_html = create_health_chart(df, chart_type)
    
    return jsonify({'chart': chart_html})

@app.route('/api/export', methods=['POST'])
def export():
    """Export filtered data"""
    tool_type = request.json.get('tool_type')
    export_format = request.json.get('format', 'csv')
    filters = request.json.get('filters', {})
    
    df = data_store[tool_type]
    filtered_df = dynamic_filter(df, tool_type, filters)
    
    if export_format == 'csv':
        return jsonify({
            'data': filtered_df.to_csv(index=False),
            'filename': f'{tool_type}_data.csv'
        })
    elif export_format == 'json':
        return jsonify({
            'data': filtered_df.to_json(orient='records'),
            'filename': f'{tool_type}_data.json'
        })

@app.route('/api/statistics', methods=['POST'])
def get_full_statistics():
    """Get comprehensive statistics"""
    tool_type = request.json.get('tool_type')
    filters = request.json.get('filters', {})
    
    df = data_store[tool_type]
    filtered_df = dynamic_filter(df, tool_type, filters)
    
    stats = get_statistics(filtered_df, tool_type)
    recommendations = get_recommendations(filtered_df, tool_type)
    
    return jsonify({
        'statistics': stats,
        'recommendations': recommendations
    })

@app.route('/api/health_analyzer', methods=['POST'])
def health_analyzer():
    """Analyze individual health condition based on user input"""
    try:
        age = int(request.json.get('age', 30))
        cholesterol = int(request.json.get('cholesterol', 180))
        blood_pressure = request.json.get('blood_pressure', '120/80')
        
        diagnosis = analyze_health_condition(age, cholesterol, blood_pressure)
        
        return jsonify({
            'success': True,
            'diagnosis': diagnosis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/upload_health_data', methods=['POST'])
def upload_health_data():
    """Upload and process health data file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only CSV and Excel files allowed'}), 400
        
        # Read file
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error reading file: {str(e)}'}), 400
        
        # Validate data
        if df.empty:
            return jsonify({'success': False, 'error': 'File is empty'}), 400
        
        # Sanitize data
        df = sanitize_data(df)
        
        # Store in data_store
        data_store['health'] = df
        
        # Get stats
        stats = get_statistics(df, 'health')
        
        return jsonify({
            'success': True,
            'message': f'Uploaded {len(df)} health records successfully!',
            'columns': list(df.columns),
            'rows': len(df),
            'stats': stats,
            'preview': df.head(10).to_dict(orient='records')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
