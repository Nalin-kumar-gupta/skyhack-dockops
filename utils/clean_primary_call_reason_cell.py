import logging

def clean_primary_call_reason(ccasr):
    logging.info("Cleaning 'primary_call_reason' column in the dataset...")

    # Replace NaNs with empty strings and convert to lowercase
    ccasr['primary_call_reason'] = ccasr['primary_call_reason'].fillna('').astype(str).str.lower()

    # Remove special characters
    logging.info("Removing special characters from 'primary_call_reason'...")
    ccasr['primary_call_reason'] = ccasr['primary_call_reason'].str.replace(r'[^\w\s]', '', regex=True)

    # Remove stopwords
    stop_words = ['and']
    logging.info("Removing stopwords from 'primary_call_reason'...")
    ccasr['primary_call_reason'] = ccasr['primary_call_reason'].apply(
        lambda x: ' '.join(word for word in x.split() if word not in stop_words)
    )

    # Remove extra spaces
    logging.info("Removing extra spaces from 'primary_call_reason'...")
    ccasr['primary_call_reason'] = ccasr['primary_call_reason'].str.replace(r'\s+', '', regex=True)

    # Replace empty values with 'othertopics'
    logging.info("Replacing empty values in 'primary_call_reason' with 'othertopics'...")
    ccasr['primary_call_reason'] = ccasr['primary_call_reason'].replace('', 'othertopics')

    return ccasr