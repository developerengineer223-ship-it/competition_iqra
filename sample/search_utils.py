import pandas as pd
from typing import List
import re

def search_patients(df: pd.DataFrame, query: str, max_results: int = 20) -> List[dict]:
    query = query.strip().lower()
    if len(query) < 2:
        return []
    # Fuzzy match name
    def match_name(name):
        return query in name.lower() or re.sub(r'[^a-z]', '', query) in re.sub(r'[^a-z]', '', name.lower())
    # Exact ID match
    def match_id(pid):
        return str(pid) == query
    # Condition match
    def match_condition(cond):
        return query in str(cond).lower()
    results = []
    for _, row in df.iterrows():
        if match_id(row['patient_id']) or match_name(row['name']) or match_condition(row['condition']):
            results.append({
                'name': row['name'],
                'patient_id': row['patient_id'],
                'condition': row['condition']
            })
        if len(results) >= max_results:
            break
    # Prioritize exact matches
    results.sort(key=lambda r: (
        str(r['patient_id']) == query,
        r['name'].lower() == query,
        query in r['name'].lower(),
        query in str(r['condition']).lower()
    ), reverse=True)
    return results
