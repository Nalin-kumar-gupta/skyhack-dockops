import pandas as pd

# Read the merged dataset (adjust the file path and format as needed)
df = pd.read_csv('output/processed_dataset_with_ext1.csv')

# Step 1: Replace NaNs with empty strings and convert to lowercase
df['primary_call_reason'] = df['primary_call_reason'].fillna('').astype(str).str.lower()

# List of stopwords to remove
# stop_words = ['and', 'or', 'etc', 'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of']
stop_words = ['and']

# Step 2: Remove special characters
df['primary_call_reason'] = df['primary_call_reason'].str.replace(r'[^\w\s]', '', regex=True)

# Step 3: Remove stopwords
df['primary_call_reason'] = df['primary_call_reason'].apply(
    lambda x: ' '.join(word for word in x.split() if word not in stop_words)
)

# Step 4: Remove spaces (if any remain)
df['primary_call_reason'] = df['primary_call_reason'].str.replace(r'\s+', '', regex=True)

# Step 5: Replace empty values with 'othertopics'
df['primary_call_reason'] = df['primary_call_reason'].replace('', 'othertopics')

# Write the corrected dataframe to a new CSV file
df.to_csv('output/processed_dataset_with_ext.csv', index=False)