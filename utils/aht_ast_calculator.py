import pandas as pd
import logging

def calculate_aht_ast(df):
    df['call_start_datetime'] = pd.to_datetime(df['call_start_datetime'], format='%m/%d/%Y %H:%M')
    df['agent_assigned_datetime'] = pd.to_datetime(df['agent_assigned_datetime'], format='%m/%d/%Y %H:%M')
    df['call_end_datetime'] = pd.to_datetime(df['call_end_datetime'], format='%m/%d/%Y %H:%M')

    df['aht'] = (df['call_end_datetime'] - df['call_start_datetime']).dt.total_seconds() / 60
    df['ast'] = (df['agent_assigned_datetime'] - df['call_start_datetime']).dt.total_seconds() / 60
    df['call_date'] = df['call_start_datetime'].dt.date

    return df