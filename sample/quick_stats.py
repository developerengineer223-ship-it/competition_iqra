import pandas as pd
from typing import Dict, Any

def quick_stats_dashboard(df: pd.DataFrame) -> Dict[str, Any]:
    stats = {}
    # 1. Record statistics
    stats['total_records'] = len(df)
    stats['unique_patients'] = df['patient_id'].nunique()
    stats['date_range'] = (str(df['date'].min().date()), str(df['date'].max().date())) if not df.empty else ('', '')
    # 2. Heart rate
    stats['heart_rate'] = {
        'mean': df['heart_rate'].mean(),
        'min': df['heart_rate'].min(),
        'max': df['heart_rate'].max(),
        'median': df['heart_rate'].median(),
        'std': df['heart_rate'].std(),
        'normal_count': df[(df['heart_rate'] >= 60) & (df['heart_rate'] <= 100)].shape[0],
        'normal_pct': 100 * df[(df['heart_rate'] >= 60) & (df['heart_rate'] <= 100)].shape[0] / max(1, len(df)),
        'abnormal_count': df[(df['heart_rate'] < 60) | (df['heart_rate'] > 100)].shape[0]
    }
    # 3. Blood pressure
    stats['blood_pressure'] = {
        'normal': df[(df['bp_systolic'] < 120) & (df['bp_diastolic'] < 80)].shape[0],
        'elevated': df[(df['bp_systolic'].between(120, 139)) & (df['bp_diastolic'] < 90)].shape[0],
        'high': df[(df['bp_systolic'] >= 140) | (df['bp_diastolic'] >= 90)].shape[0],
    }
    # 4. Cholesterol
    stats['cholesterol'] = {
        'mean': df['cholesterol'].mean(),
        'min': df['cholesterol'].min(),
        'max': df['cholesterol'].max(),
        'desirable': df[df['cholesterol'] < 200].shape[0],
        'borderline': df[df['cholesterol'].between(200, 239)].shape[0],
        'high': df[df['cholesterol'] >= 240].shape[0],
        'high_pct': 100 * df[df['cholesterol'] >= 240].shape[0] / max(1, len(df))
    }
    # 5. Stress level
    stats['stress_level'] = df['stress_level'].value_counts(normalize=True).to_dict()
    # 6. Condition
    stats['condition'] = df['condition'].value_counts(normalize=True).to_dict()
    # 7. Risk assessment
    stats['risk'] = {
        'low': df[df['risk_score'] <= 33].shape[0],
        'medium': df[(df['risk_score'] > 33) & (df['risk_score'] <= 66)].shape[0],
        'high': df[(df['risk_score'] > 66) & (df['risk_score'] < 100)].shape[0],
        'critical': df[df['validation_status'] == 'Critical'].shape[0]
    }
    # 8. Demographics
    stats['age'] = {
        'mean': df['age'].mean(),
        'min': df['age'].min(),
        'max': df['age'].max(),
        'groups': df['age'].value_counts(bins=[18,30,40,50,60,70,120]).to_dict()
    }
    stats['gender'] = df['gender'].value_counts(normalize=True).to_dict()
    # 9. Data quality
    complete = df.dropna().shape[0]
    incomplete = len(df) - complete
    stats['data_quality'] = {
        'complete': complete,
        'incomplete': incomplete,
        'completeness_pct': 100 * complete / max(1, len(df)),
        'missing_by_col': df.isna().sum().to_dict()
    }
    # 10. Alerts
    stats['alerts'] = {
        'critical_bp': df[(df['bp_systolic'] > 180) | (df['bp_diastolic'] > 120)].shape[0],
        'high_cholesterol': df[df['cholesterol'] > 240].shape[0],
        'high_stress': df[df['stress_level'] == 'High'].shape[0],
        'abnormal_hr': df[(df['heart_rate'] < 40) | (df['heart_rate'] > 140)].shape[0]
    }
    return stats
