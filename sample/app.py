from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
from sanitize_health_data import sanitize_health_data

app = Flask(__name__)

# Load and clean data at startup (sample data for demo)
sample_data = {
    'patient_id': [1, 2, 1, 3, 4, 5],
    'name': ['John Doe', 'Jane Roe', 'John Doe', 'Alice', 'Bob', 'Charlie'],
    'age': [45, 50, 45, 60, 35, 70],
    'gender': ['M', 'F', 'M', 'F', 'M', 'Other'],
    'heart_rate': [80, 90, 85, 72, 110, 65],
    'blood_pressure': ['120/80', '130/85', '125/82', '140/90', '135/88', '118/78'],
    'cholesterol': [180, 220, 190, 250, 210, 170],
    'stress_level': ['Medium', 'High', 'Medium', 'Low', 'Medium', 'High'],
    'condition': ['Normal', 'High-Risk', 'Normal', 'Pre-hypertension', 'Diabetes', 'Normal'],
    'date': ['2024-01-01', '2024-01-02', '2024-02-01', '2024-03-01', '2024-03-15', '2024-04-01'],
    'medical_history': ['None', 'Asthma', 'None', 'Hypertension', 'Diabetes', 'None']
}
raw_df = pd.DataFrame(sample_data)
raw_df['date'] = pd.to_datetime(raw_df['date'])
df, quality_report = sanitize_health_data(raw_df)

# Dashboard route
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Helper: get filter schema
def get_filter_schema():
    return {
        'age': {'min': 18, 'max': 80, 'step': 5},
        'condition': ['Normal', 'Pre-hypertension', 'High-Risk', 'Diabetes'],
        'stress_level': ['Low', 'Medium', 'High'],
        'date': {'min': str(df['date'].min().date()) if not df.empty else '', 'max': str(df['date'].max().date()) if not df.empty else ''},
        'gender': ['M', 'F', 'Other']
    }

@app.route('/api/filters/schema', methods=['GET'])
def filter_schema():
    return jsonify(get_filter_schema())

@app.route('/api/filters/apply', methods=['POST'])
def apply_filters():
    filters = request.json or {}
    filtered = df.copy()
    # Age filter
    if 'age' in filters:
        min_age, max_age = filters['age']
        filtered = filtered[(filtered['age'] >= min_age) & (filtered['age'] <= max_age)]
    # Condition filter
    if 'condition' in filters and filters['condition']:
        filtered = filtered[filtered['condition'].isin(filters['condition'])]
    # Stress level filter
    if 'stress_level' in filters and filters['stress_level']:
        filtered = filtered[filtered['stress_level'].isin(filters['stress_level'])]
    # Date range filter
    if 'date' in filters:
        start, end = pd.to_datetime(filters['date'][0]), pd.to_datetime(filters['date'][1])
        filtered = filtered[(filtered['date'] >= start) & (filtered['date'] <= end)]
    # Gender filter
    if 'gender' in filters and filters['gender']:
        filtered = filtered[filtered['gender'].isin(filters['gender'])]
    # Pagination
    page = int(filters.get('page', 1))
    per_page = int(filters.get('per_page', 50))
    total = len(filtered)
    filtered_page = filtered.iloc[(page-1)*per_page: page*per_page]
    # Statistics
    stats = {
        'avg_heart_rate': filtered['heart_rate'].mean() if not filtered.empty else None,
        'avg_bp_systolic': filtered['bp_systolic'].mean() if not filtered.empty else None,
        'avg_bp_diastolic': filtered['bp_diastolic'].mean() if not filtered.empty else None,
        'most_common_condition': filtered['condition'].mode()[0] if not filtered.empty and not filtered['condition'].mode().empty else None,
        'avg_stress_level': filtered['stress_level'].mode()[0] if not filtered.empty and not filtered['stress_level'].mode().empty else None,
        'filtered_count': total
    }
    return jsonify({
        'records': filtered_page.to_dict(orient='records'),
        'total': total,
        'page': page,
        'per_page': per_page,
        'stats': stats
    })

@app.route('/api/filters/export', methods=['GET'])
def export_filtered():
    # For demo, export all cleaned data as CSV
    export_format = request.args.get('format', 'csv')
    export_df = df.copy()  # In real use, apply filters from session or request
    filename = f"health_report_export.{export_format}"
    if export_format == 'csv':
        export_df.to_csv(filename, index=False)
        return send_file(filename, as_attachment=True)
    elif export_format == 'xlsx':
        with pd.ExcelWriter(filename) as writer:
            export_df.to_excel(writer, sheet_name='Patient Data', index=False)
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({'error': 'Unsupported format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
