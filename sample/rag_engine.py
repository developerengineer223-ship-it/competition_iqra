import pandas as pd
from typing import Dict, Any

def retrieve_patient_context(df: pd.DataFrame, patient_id: int) -> Dict[str, Any]:
    """
    Retrieves all context needed for RAG-based recommendation for a given patient.
    Returns a dict with patient profile, similar cases, guidelines, trends, and cohort stats.
    """
    context = {}
    # 1. Patient profile
    patient = df[df['patient_id'] == patient_id].sort_values('date').iloc[-1]
    context['patient_profile'] = patient.to_dict()
    # 2. Similar patients
    similar = df[(df['age'].between(patient['age']-5, patient['age']+5)) &
                 (df['condition'] == patient['condition']) &
                 (df['stress_level'] == patient['stress_level']) &
                 (df['patient_id'] != patient_id)]
    top_similar = similar.sort_values('date', ascending=False).head(5)
    context['similar_cases'] = top_similar.to_dict(orient='records')
    # 3. Medical guidelines (stub, replace with real lookup)
    guidelines = {
        'heart_rate': '60-100 bpm',
        'bp': '<120/80 mmHg',
        'cholesterol': '<200 mg/dL',
        'lifestyle': 'Exercise, healthy diet, stress management',
        'monitoring': 'Check vitals monthly',
        'emergency': 'Seek care if chest pain, severe headache, or fainting'
    }
    context['guidelines'] = guidelines
    # 4. Historical trends
    patient_history = df[df['patient_id'] == patient_id].sort_values('date')
    context['trends'] = {
        'heart_rate': patient_history['heart_rate'].tolist(),
        'bp_systolic': patient_history['bp_systolic'].tolist(),
        'bp_diastolic': patient_history['bp_diastolic'].tolist(),
        'dates': patient_history['date'].astype(str).tolist()
    }
    # 5. Cohort stats
    cohort = df[df['condition'] == patient['condition']]
    context['cohort_stats'] = {
        'success_rate': 0.85,  # Placeholder
        'avg_time_to_improve': 30,  # days, placeholder
        'common_comorbidities': ['Hypertension'],
        'most_effective_treatment': 'Lifestyle modification',
        'failure_rate': 0.1
    }
    return context

# Example LLM prompt formatting
def format_rag_prompt(context: Dict[str, Any]) -> str:
    """
    Formats the RAG context into a prompt for LLM.
    """
    patient = context['patient_profile']
    guidelines = context['guidelines']
    similar = context['similar_cases']
    trends = context['trends']
    cohort = context['cohort_stats']
    prompt = f"""
Patient: {patient['name']} (ID: {patient['patient_id']}, Age: {patient['age']}, Gender: {patient['gender']})\n
Current Metrics:\n- Heart Rate: {patient['heart_rate']} bpm\n- Blood Pressure: {patient['bp_systolic']}/{patient['bp_diastolic']} mmHg\n- Cholesterol: {patient['cholesterol']} mg/dL\n- Stress Level: {patient['stress_level']}\n- Condition: {patient['condition']}\n- Risk Score: {patient['risk_score']}\n\nMedical Guidelines:\n- Heart Rate: {guidelines['heart_rate']}\n- Blood Pressure: {guidelines['bp']}\n- Cholesterol: {guidelines['cholesterol']}\n- Lifestyle: {guidelines['lifestyle']}\n- Monitoring: {guidelines['monitoring']}\n- Emergency: {guidelines['emergency']}\n\nSimilar Cases:\n"""
    for case in similar:
        prompt += f"- Age: {case['age']}, Condition: {case['condition']}, Outcome: Improved\n"
    prompt += f"\nTrends (last 3-6 months):\n- Heart Rate: {trends['heart_rate']}\n- BP Systolic: {trends['bp_systolic']}\n- BP Diastolic: {trends['bp_diastolic']}\n\nCohort Stats:\n- Success Rate: {cohort['success_rate']}\n- Avg Time to Improve: {cohort['avg_time_to_improve']} days\n- Most Effective Treatment: {cohort['most_effective_treatment']}\n\nGenerate a personalized, evidence-based health recommendation for this patient.\nInclude risk level, 3-5 specific actions, monitoring plan, emergency signs, and cite sources.\nAlways include a disclaimer to consult a healthcare provider.\n"""
    return prompt


# Demo/test block for direct execution
if __name__ == "__main__":
    # Example DataFrame for testing
    import pandas as pd
    data = {
        'patient_id': [1, 2, 1],
        'name': ['John Doe', 'Jane Roe', 'John Doe'],
        'age': [45, 50, 45],
        'gender': ['M', 'F', 'M'],
        'heart_rate': [80, 90, 85],
        'blood_pressure': ['120/80', '130/85', '125/82'],
        'cholesterol': [180, 220, 190],
        'stress_level': ['Medium', 'High', 'Medium'],
        'condition': ['Normal', 'High-Risk', 'Normal'],
        'date': ['2024-01-01', '2024-01-02', '2024-02-01'],
        'bp_systolic': [120, 130, 125],
        'bp_diastolic': [80, 85, 82],
        'risk_score': [20, 70, 25]
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    context = retrieve_patient_context(df, 1)
    prompt = format_rag_prompt(context)
    print(prompt)
