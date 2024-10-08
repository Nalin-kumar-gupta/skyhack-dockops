import numpy as np
import pandas as pd

calls=pd.read_csv('data/calls.csv')
customers=pd.read_csv('data/customers.csv')
reason=pd.read_csv('data/reason.csv')
sentiment=pd.read_csv('data/sentiment.csv')

cas=pd.merge(calls,sentiment,on='call_id',how='left')
print(cas.isnull().sum())

casr=pd.merge(cas,reason,on='call_id',how='left')
print(casr.isnull().sum())

ccasr=pd.merge(casr,customers,on='customer_id',how='left')
print(ccasr.isnull().sum())

ccasr.to_csv('data/merged_data.csv')