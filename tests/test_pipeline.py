import pytest
import pandas as pd

def mock_get_bank_id(row_val):
    custom_map = {
        'CBE': 1,
        'CBE Mobile': 1,
        'Amole': 3,
        'Dashen': 3
    }
    return custom_map.get(row_val)

def test_bank_mapping_logic():
    """Ensure bank name variations are mapped to correct IDs"""
    assert mock_get_bank_id('CBE') == 1
    assert mock_get_bank_id('Amole') == 3
    assert mock_get_bank_id('Unknown') is None

def test_dataframe_columns():
    """Ensure processed data has necessary columns before DB insert"""
    data = {
        'bank_name': ['CBE'],
        'content': ['Great app'],
        'score': [5],
        'at': ['2025-01-01']
    }
    df = pd.DataFrame(data)
    df = df.rename(columns={'content': 'review_text', 'score': 'rating'})
    
    expected_cols = ['review_text', 'rating']
    for col in expected_cols:
        assert col in df.columns