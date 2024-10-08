import numpy as np
import pandas as pd
import logging
import spacy
import os
import re

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load spaCy's English model
logging.info("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

# Step 1: Read CSV Files
logging.info("Reading CSV files...")
calls = pd.read_csv('data/calls.csv')
customers = pd.read_csv('data/customers.csv')
reasons = pd.read_csv('data/reason.csv')
sentiments = pd.read_csv('data/sentiment.csv')

# Step 2: Merge Calls and Sentiments
logging.info("Merging 'calls' with 'sentiments' on 'call_id'...")
cas = pd.merge(calls, sentiments, on='call_id', how='left')
logging.info(f"Null values after merging 'calls' and 'sentiments':\n{cas.isnull().sum()}")

# Step 3: Merge with Reasons
logging.info("Merging 'cas' with 'reasons' on 'call_id'...")
casr = pd.merge(cas, reasons, on='call_id', how='left')
logging.info(f"Null values after merging 'cas' and 'reasons':\n{casr.isnull().sum()}")

# Step 4: Merge with Customers
logging.info("Merging 'casr' with 'customers' on 'customer_id'...")
ccasr = pd.merge(casr, customers, on='customer_id', how='left')
logging.info(f"Null values after merging 'casr' and 'customers':\n{ccasr.isnull().sum()}")

# Step 5: Extract 'travelling_from' and 'travelling_to' from 'call_transcript'
# Function to extract the first city pair
def extract_first_city_pair(transcript):
    # Convert transcript to lowercase for case-insensitive search
    lower_transcript = str(transcript).lower()  # Convert to string to avoid errors

    # Start searching from the beginning of the transcript
    search_index = 0
    
    while True:
        # Find the start of "from"
        from_index = lower_transcript.find('from ', search_index)
        if from_index == -1:
            return None, None  # No more "from" found

        # Find the start of "to" after "from"
        to_index = lower_transcript.find(' to ', from_index)
        if to_index == -1:
            return None, None  # No "to" found after "from"
        
        # Extract words between "from" and "to"
        words_between = lower_transcript[from_index + 5:to_index].strip().split()
        
        # Check if the words in between are more than 4
        if len(words_between) > 4:
            # Move search index to the next occurrence of "from"
            search_index = to_index + 4
            continue  # Skip to the next "from"
        
        # Extract "from" city
        from_city = ' '.join(words_between).title()  # Capitalize first letter of each word
        
        # Extract words after "to"
        words_after_to = lower_transcript[to_index + 4:].strip().split()
        
        # Remove unwanted words after the "to" keyword and limit words
        unwanted_words = [
            'next', 'for', 'was', 'is', 'will', 'tomorrow', 'and', 'scheduled', 
            'last', 'week', 'month', 'year', 'yesterday', 'today', 'day', 'then', 
            'later', 'around', 'via', 'towards', 'approximately', 'arriving', 'departing', 
            'going', 'leaving', 'back', 'trip', 'meeting', 'visit', 'returning', 'morning', 
            'evening', 'afternoon', 'night', 'am', 'pm', 'that', 'agent', 'Agent', 'on', 'On'
        ]
        to_city_words = []
        for word in words_after_to:
            # Stop processing if the word or its variation with period or comma is in unwanted words
            if word.rstrip('.,') in unwanted_words:
                break
            
            # Clean special characters (e.g., '.', ',', etc.) within or at the end of the word
            # Match any character that is not a letter or space and remove everything after it
            cleaned_word = re.sub(r'[^a-zA-Z\s].*', '', word)
            
            # If the cleaned word is valid (not empty), append it to to_city_words
            if cleaned_word:
                to_city_words.append(cleaned_word)

            # Stop if we already have 2 words
            if len(to_city_words) >= 2:
                break
        
        # Join and clean the "to" city
        to_city = ' '.join(to_city_words).strip().title()  # Capitalize first letter of each word

        # Special case for "la"
        if to_city.lower() == 'la':
            to_city = 'Los Angeles'
        if from_city.lower() == 'la':
            from_city = 'Los Angeles'
        if to_city.lower() == 'nyc':
            to_city = 'New York'
        if from_city.lower() == 'nyc':
            from_city = 'New York'
        if to_city.lower() == 'lax':
            to_city = 'Los Angeles'
        if from_city.lower() == 'lax':
            from_city = 'Los Angeles'
            

        return from_city, to_city

logging.info("Extracting 'travelling_from' and 'travelling_to' locations from 'call_transcript'...")
ccasr[['travelling_from', 'travelling_to']] = ccasr['call_transcript'].apply(
    lambda x: pd.Series(extract_first_city_pair(x))
)

# # Step 6: Correct 'travelling_from' and 'travelling_to' using spaCy for validation
# def extract_location(text):
#     if pd.isna(text):  # Handle NaN cases
#         return ""
    
#     doc = nlp(text)
    
#     # Extract GPE (Geopolitical Entity) from the text
#     for ent in doc.ents:
#         if ent.label_ == "GPE":
#             return ent.text
    
#     return ""

# logging.info("Correcting 'travelling_from' and 'travelling_to' locations using spaCy...")
# ccasr['travelling_from'] = ccasr['travelling_from'].apply(lambda x: extract_location(x))
# ccasr['travelling_to'] = ccasr['travelling_to'].apply(lambda x: extract_location(x))

# Step 7: Extract call reason, agent solutions, and customer response from transcripts
def extract_info(transcript):
    call_reason = []
    agent_solutions = []
    customer_responses = []

    lines = transcript.split('\n')
    capturing_reason = False
    capturing_solutions = False
    
    for line in lines:
        if "Customer" in line and "I'm calling" in line:
            capturing_reason = True
            reason_part = line.split("I'm calling")[-1].strip()
            call_reason.append(reason_part)
        
        if "Agent" in line and capturing_reason:
            capturing_reason = False
        
        if capturing_reason:
            call_reason.append(line.strip())
        
        if "Agent" in line and "Let me" in line:
            capturing_solutions = True
            solution_part = line.split("Let me")[-1].strip()
            agent_solutions.append("Let me " + solution_part)
        
        if "Customer" in line:
            capturing_solutions = False
            customer_responses.append(line.strip())

    if len(customer_responses) >= 2:
        customer_accepted = customer_responses[-2]
    elif len(customer_responses) == 1:
        customer_accepted = customer_responses[0]
    else:
        customer_accepted = "No customer response found"

    formatted_solutions = [f"Solution {i+1}: {sol}" for i, sol in enumerate(agent_solutions)]
    
    return {
        "actual_call_reason": " | ".join(call_reason),
        "agent_solutions": " | ".join(formatted_solutions),
        "customer_accepted": customer_accepted
    }

logging.info("Extracting call reason, solutions, and customer responses from transcripts...")
df_extracted = ccasr['call_transcript'].apply(extract_info)
extracted_df = pd.DataFrame(list(df_extracted))
ccasr = pd.concat([ccasr, extracted_df], axis=1)

# Step 8: Categorize based on 'actual_call_reason'
def categorize_reason(call_reason):
    if pd.isna(call_reason) or call_reason.strip() == "":
        return 'Miscellaneous Issue'

    call_reason = call_reason.lower().strip()

    if call_reason.startswith("to complain"):
        return 'Complaint'
    elif call_reason.startswith("to inquire"):
        return 'Get Details'
    elif call_reason.startswith("about") or call_reason.startswith("regarding"):
        return 'Get Details'
    elif call_reason.startswith("because") or call_reason.startswith("cause"):
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' and 'missed' in call_reason:
                return 'Miss Connecting Flight'
            else:
                return 'Delayed Flight'
        else:
            if 'complain' or 'complaint' in call_reason:
                return 'Complaint'
            return 'Miscellaneous Issue'
    
    return 'Miscellaneous Issue'

logging.info("Categorizing based on 'actual_call_reason'...")
ccasr['reason_label'] = ccasr['actual_call_reason'].apply(categorize_reason)

# Step 9: Calculate AHT, AST, and extract Call Date
logging.info("Calculating AHT, AST, and extracting 'call_date'...")
def calculate_aht_ast(df):
    df['call_start_datetime'] = pd.to_datetime(df['call_start_datetime'], format='%m/%d/%Y %H:%M')
    df['agent_assigned_datetime'] = pd.to_datetime(df['agent_assigned_datetime'], format='%m/%d/%Y %H:%M')
    df['call_end_datetime'] = pd.to_datetime(df['call_end_datetime'], format='%m/%d/%Y %H:%M')

    df['aht'] = (df['call_end_datetime'] - df['call_start_datetime']).dt.total_seconds() / 60
    df['ast'] = (df['agent_assigned_datetime'] - df['call_start_datetime']).dt.total_seconds() / 60
    df['call_date'] = df['call_start_datetime'].dt.date

    return df

ccasr = calculate_aht_ast(ccasr)

# Step 10: Save Final Dataset
output_file = 'data/final_corrected_dataset_with_aht_ast.csv'
logging.info(f"Saving the final dataset to {output_file}...")
ccasr.to_csv(output_file, index=False)
logging.info("Process completed successfully.")