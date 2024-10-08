import pandas as pd
import logging

def merge_data(calls, sentiments, reasons, customers):
    logging.info("Merging 'calls' with 'sentiments' on 'call_id'...")
    cas = pd.merge(calls, sentiments, on='call_id', how='left')
    logging.debug(f"After merging 'calls' and 'sentiments', shape: {cas.shape}, Null counts:\n{cas.isnull().sum()}")

    logging.info("Merging 'cas' with 'reasons' on 'call_id'...")
    casr = pd.merge(cas, reasons, on='call_id', how='left')
    logging.debug(f"After merging 'cas' with 'reasons', shape: {casr.shape}, Null counts:\n{casr.isnull().sum()}")

    logging.info("Merging 'casr' with 'customers' on 'customer_id'...")
    ccasr = pd.merge(casr, customers, on='customer_id', how='left')
    logging.debug(f"After merging 'casr' with 'customers', shape: {ccasr.shape}, Null counts:\n{ccasr.isnull().sum()}")

    return ccasr