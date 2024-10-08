import pandas as pd
import logging

def load_csv_data():
    logging.info("Reading CSV files...")
    calls = pd.read_csv('data/calls.csv')
    customers = pd.read_csv('data/customers.csv')
    reasons = pd.read_csv('data/reason.csv')
    sentiments = pd.read_csv('data/sentiment.csv')

    logging.debug(f"Calls data shape: {calls.shape}, Sample:\n{calls.head()}")
    logging.debug(f"Customers data shape: {customers.shape}, Sample:\n{customers.head()}")
    logging.debug(f"Reasons data shape: {reasons.shape}, Sample:\n{reasons.head()}")
    logging.debug(f"Sentiments data shape: {sentiments.shape}, Sample:\n{sentiments.head()}")
    
    return calls, customers, reasons, sentiments