import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def sanitize_health_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans and validates a raw health dataset according to strict medical data quality rules.
    Returns the cleaned DataFrame and a comprehensive quality report.
    """
    report = {
        'input_rows': len(df),
        'output_rows': None,
        'duplicates_removed': 0,
        'invalid_rows_removed': 0,
        'missing_filled': {},
        'data_quality_score': None,
        'validation_issues': [],
        'columns_with_missing': {},
    }
    df = df.copy()
    # 1. Handle missing values
    numeric_cols = ['heart_rate', 'cholesterol', 'age']
    categorical_cols = ['stress_level', 'condition']
    text_cols = ['name', 'medical_history']
    critical_cols = ['heart_rate', 'blood_pressure', 'cholesterol', 'stress_level', 'condition']
    # Fill numeric columns
    for col in numeric_cols:
        missing = df[col].isna().sum()
        if missing > 0:
            if missing / len(df) < 0.05:
                fill_value = df[col].median() if df[col].dtype != object else pd.to_numeric(df[col], errors='coerce').median()
                df[col] = df[col].fillna(fill_value)
                report['missing_filled'][col] = missing
            else:
                report['columns_with_missing'][col] = missing
    # Fill categorical columns
    for col in categorical_cols:
        missing = df[col].isna().sum()
        if missing > 0:
            if missing / len(df) < 0.05:
                fill_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                df[col] = df[col].fillna(fill_value)
                report['missing_filled'][col] = missing
            else:
                df[col] = df[col].fillna('Unknown')
                report['missing_filled'][col] = missing
    # Fill text columns
    for col in text_cols:
        missing = df[col].isna().sum()
        if missing > 0:
            df[col] = df[col].fillna('Not Provided')
            report['missing_filled'][col] = missing
    # Remove rows with >20% missing in critical columns
    thresh = int(len(critical_cols) * 0.8)
    before = len(df)
    df = df.dropna(subset=critical_cols, thresh=thresh)
    report['invalid_rows_removed'] = before - len(df)
    # 2. Remove duplicates
    before = len(df)
    df = df.sort_values('date').drop_duplicates(['patient_id', 'date'], keep='last')
    report['duplicates_removed'] = before - len(df)
    # 3. Data type conversion
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df['patient_id'] = pd.to_numeric(df['patient_id'], errors='coerce')
    df['cholesterol'] = pd.to_numeric(df['cholesterol'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Blood pressure: split systolic/diastolic
    bp_split = df['blood_pressure'].str.extract(r'(\d{2,3})\s*/\s*(\d{2,3})')
    df['bp_systolic'] = pd.to_numeric(bp_split[0], errors='coerce')
    df['bp_diastolic'] = pd.to_numeric(bp_split[1], errors='coerce')
    # Heart rate
    df['heart_rate'] = pd.to_numeric(df['heart_rate'], errors='coerce')
    # Standardize stress_level
    df['stress_level'] = df['stress_level'].str.strip().str.title().replace({'Low': 'Low', 'Medium': 'Medium', 'High': 'High'}).fillna('Unknown')
    # Standardize condition
    cond_map = {'high bp': 'High-Risk', 'diabetes': 'Diabetes', 'pre-hypertension': 'Pre-hypertension', 'normal': 'Normal'}
    df['condition'] = df['condition'].str.strip().str.title().replace(cond_map)
    # Standardize gender
    df['gender'] = df['gender'].str.upper().map({'M': 'M', 'F': 'F', 'O': 'Other', 'OTHER': 'Other'}).fillna('Other')
    # 4. String standardization
    df['name'] = df['name'].str.title().str.replace(r'[^a-zA-Z\s]', '', regex=True).str.strip()
    # 5. Data validation & outlier detection
    def validate_row(row):
        status = 'Valid'
        issues = []
        risk_score = 0
        # Heart rate
        if not (30 <= row['heart_rate'] <= 200):
            status = 'Critical'
            issues.append('Abnormal heart rate')
            risk_score += 30
        elif row['heart_rate'] < 40 or row['heart_rate'] > 140:
            status = 'Warning'
            issues.append('Heart rate warning')
            risk_score += 10
        # Blood pressure
        if not (70 <= row['bp_systolic'] <= 200) or not (40 <= row['bp_diastolic'] <= 130):
            status = 'Critical'
            issues.append('Abnormal blood pressure')
            risk_score += 30
        elif row['bp_systolic'] >= 140 or row['bp_diastolic'] >= 90:
            status = 'Warning'
            issues.append('High blood pressure')
            risk_score += 10
        # Cholesterol
        if not (100 <= row['cholesterol'] <= 400):
            status = 'Critical'
            issues.append('Abnormal cholesterol')
            risk_score += 20
        elif row['cholesterol'] > 240:
            status = 'Warning'
            issues.append('High cholesterol')
            risk_score += 10
        # Age
        if not (1 <= row['age'] <= 120):
            status = 'Critical'
            issues.append('Abnormal age')
            risk_score += 10
        # Stress level
        if row['stress_level'] not in ['Low', 'Medium', 'High']:
            status = 'Warning'
            issues.append('Unknown stress level')
        # Risk score normalization
        risk_score = min(100, risk_score)
        return pd.Series({'validation_status': status, 'validation_issues': '; '.join(issues), 'risk_score': risk_score})
    val = df.apply(validate_row, axis=1)
    df = pd.concat([df, val], axis=1)
    # 6. Output & reporting
    report['output_rows'] = len(df)
    report['data_quality_score'] = 100 - (report['invalid_rows_removed'] + report['duplicates_removed']) / max(1, report['input_rows']) * 100
    report['validation_issues'] = df[df['validation_status'] != 'Valid']['validation_issues'].tolist()
    for col in critical_cols:
        report['columns_with_missing'][col] = int(df[col].isna().sum())
    return df, report
