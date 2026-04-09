import plotly.graph_objs as go
import pandas as pd

def bar_chart_heart_rate_by_age(df: pd.DataFrame):
    bins = [18, 30, 40, 50, 60, 70, 120]
    labels = ['18-30', '30-40', '40-50', '50-60', '60-70', '70+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    grouped = df.groupby('age_group')['heart_rate'].mean().reindex(labels)
    colors = ['green' if 60 <= hr <= 100 else 'yellow' if 100 < hr <= 120 or 40 <= hr < 60 else 'red' for hr in grouped]
    fig = go.Figure([go.Bar(x=labels, y=grouped, marker_color=colors,
                            hovertext=[f"Age: {l}, Avg HR: {v:.1f}" for l, v in zip(labels, grouped)])])
    fig.add_shape(type='line', x0=-0.5, x1=5.5, y0=60, y1=60, line=dict(color='blue', dash='dash'))
    fig.add_shape(type='line', x0=-0.5, x1=5.5, y0=100, y1=100, line=dict(color='blue', dash='dash'))
    fig.update_layout(title='Average Heart Rate by Age Group', xaxis_title='Age Group', yaxis_title='Avg Heart Rate (bpm)')
    return fig

def line_chart_bp_trend(df: pd.DataFrame, patient_id=None):
    if patient_id:
        df = df[df['patient_id'] == patient_id]
    df = df.sort_values('date')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['bp_systolic'], mode='lines+markers', name='Systolic', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['bp_diastolic'], mode='lines+markers', name='Diastolic', line=dict(color='red')))
    fig.update_layout(title='Blood Pressure Trend Over Time', xaxis_title='Date', yaxis_title='Blood Pressure (mmHg)')
    return fig

def pie_chart_stress_level(df: pd.DataFrame):
    counts = df['stress_level'].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    colors = ['green' if l == 'Low' else 'yellow' if l == 'Medium' else 'red' for l in labels]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.4, marker_colors=colors))
    fig.update_layout(title='Stress Level Distribution')
    return fig
