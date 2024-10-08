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
    capture_more_customer_lines = False  # Flag to capture extra customer lines
    
    customer_line_count = 0  # Counter for capturing the first three customer lines
    
    for line in lines:
        # Extracting call reason when customer says "I'm calling"
        if "Customer" in line and "I'm calling" in line:
            capturing_reason = True
            reason_part = line.split("I'm calling")[-1].strip()
            call_reason.append(reason_part)  # append to the list
            
            # Check if "about" or "regarding" is mentioned in the reason
            if "about" in reason_part or "regarding" in reason_part:
                capture_more_customer_lines = True  # Trigger capturing more customer lines
        
        # Capture first three customer lines after "about" or "regarding"
        if capture_more_customer_lines and "Customer" in line:
            if customer_line_count < 3:  # Capture the first three customer lines
                call_reason.append(line.strip())
                customer_line_count += 1
            else:
                capture_more_customer_lines = False  # Stop after capturing 3 lines
        
        # Stopping the capture of the call reason when agent speaks
        if "Agent" in line and capturing_reason:
            capturing_reason = False
        
        # If still capturing the reason, append the lines
        if capturing_reason:
            call_reason.append(line.strip())  # appending to the list
        
        # Capturing solutions provided by agent
        if "Agent" in line and "Let me" in line:
            capturing_solutions = True
            solution_part = line.split("Let me")[-1].strip()
            agent_solutions.append("Let me " + solution_part)
        
        # Stop capturing solutions when the customer responds
        if "Customer" in line:
            capturing_solutions = False
            customer_responses.append(line.strip())

    # If "about" or "regarding" was mentioned, add "about" to the start of the call reason
    if "about" in " ".join(call_reason).lower() or "regarding" in " ".join(call_reason).lower():
        call_reason = "about " + " | ".join(call_reason)
    else:
        call_reason = " | ".join(call_reason) if call_reason else "No specific call reason"
    
    # Handling customer accepted solution based on responses
    if len(customer_responses) >= 2:
        customer_accepted = customer_responses[-2]
    elif len(customer_responses) == 1:
        customer_accepted = customer_responses[0]
    else:
        customer_accepted = "No customer response found"

    # Formatting the solutions provided by agent
    formatted_solutions = [f"Solution {i+1}: {sol}" for i, sol in enumerate(agent_solutions)]
    
    return {
        "actual_call_reason": call_reason,
        "agent_solutions": " | ".join(formatted_solutions),  # convert the list to a string
        "customer_accepted": customer_accepted
    }

logging.info("Extracting call reason, solutions, and customer responses from transcripts...")
df_extracted = ccasr['call_transcript'].apply(extract_info)
extracted_df = pd.DataFrame(list(df_extracted))
ccasr = pd.concat([ccasr, extracted_df], axis=1)

def categorize_reason(call_reason):
    if pd.isna(call_reason) or call_reason.strip() == "":
        return 'Miscellaneous Issue'

    call_reason = call_reason.lower().strip()

    if call_reason.startswith("to complain"):
        return 'Complaint'
    elif call_reason.startswith("to inquire"):
        return 'Get Details'
    elif call_reason.startswith("about") or call_reason.startswith("regarding"):
        if 'wanted to' in call_reason and 'check' in call_reason:
            return 'Get Details'
        elif 'change' in call_reason:
            return 'Change Flight'
        elif 'complain' in call_reason or 'not happy' in call_reason or 'complaint' in call_reason:
            return 'Complaint'
        else:
            return 'Get Details'
    elif call_reason.startswith("because") or call_reason.startswith("cause"):
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' in call_reason and 'missed' in call_reason:
                return 'Missed Connecting Flight'
            else:
                return 'Delayed Flight'
        else:
            if 'complain' in call_reason or 'complaint' in call_reason:
                return 'Complaint'
            else:
                return 'Miscellaneous Issue'
    
    else:
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' in call_reason and 'missed' in call_reason:
                return 'Missed Connecting Flight'
            else:
                return 'Delayed Flight'
        else:
            if 'complain' in call_reason or 'complaint' in call_reason:
                return 'Complaint'
            else:
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

import re

# Step 8: Function to extract offers based on agent solutions for 'Delayed Flights' and other categories
def extract_offers(agent_solution, reason_label):
    agent_solution = agent_solution.lower()

    refund_offer = ""
    voucher_offer = ""
    sky_miles_bonus = ""

    # Check if the reason label is 'Delayed Flights' or another category
    if reason_label in ['Delayed Flight', 'Missed Connecting Flight', 'Complaint', 'Miscellaneous Issue']:
        # Define regex patterns for full refund and no refund
        full_refund_patterns = [
            r"happy to provide you with a full refund",
            r"happy to process that full refund",
            r"go ahead and process that full refund",
            r"happy to process a full refund",
            r"let me offer you a full refund",
            r"can offer you a full refund",
            r"processed a full refund",
            r"full refund is certainly justified",
            r"go ahead and refund",
            r"I can offer in compensation is a full refund"
        ]

        no_refund_patterns = [
            r"unfortunately",
            r"non-refundable",
            r"unable to provide a full refund",
            r"not able to offer a refund",
            r"can't offer"
        ]

        # Check if any of the full refund patterns match
        for pattern in full_refund_patterns:
            if re.search(pattern, agent_solution):
                refund_offer = "Full refund offered"
                break  # No need to check further if already refunded

        # Check if no refund was given
        if not refund_offer:
            for pattern in no_refund_patterns:
                if re.search(pattern, agent_solution):
                    refund_offer = "No refund offered"
                    break

        # Check for travel voucher or credit and extract the value if present
        if 'voucher' in agent_solution or 'credit' in agent_solution:
            # Look for multiple values with a $ sign before "voucher" or "credit"
            voucher_matches = re.findall(r'\$(\d+)', agent_solution)
            if voucher_matches:
                # Use the value found later in the text
                voucher_value = voucher_matches[-1]  # Take the last found value
                voucher_offer = f"Travel voucher {voucher_value}$ offered"
            else:
                voucher_offer = "Travel credit offered"

        # Check for SkyMiles bonus by finding a number preceding "bonus" or "sky miles"
        bonus_match = re.search(r'(\d+)\s*(bonus|sky miles)', agent_solution)
        if bonus_match:
            sky_miles_value = bonus_match.group(1)
            sky_miles_bonus = f"{sky_miles_value} SkyMiles bonus offered"
    
    else:
        # Other categories can have different logic if needed
        refund_offer = "Refund/extraction logic for other categories"
    
    # Combine refund, voucher, and SkyMiles bonus offers if present
    offers = []
    if refund_offer:
        offers.append(refund_offer)
    if voucher_offer:
        offers.append(voucher_offer)
    if sky_miles_bonus:
        offers.append(sky_miles_bonus)

    if offers:
        return "; ".join(offers)

    # Default case if no offers found
    return "No specific offer found"

# Apply the extraction logic to the 'agent_solutions' column with the reason_label passed into the function
logging.info("Extracting offers from 'agent_solutions' for 'Delayed Flights'...")
ccasr['extracted_offers'] = ccasr.apply(
    lambda row: extract_offers(row['agent_solutions'], row['reason_label']),
    axis=1
)


# Step 10: Save Final Dataset
output_file = 'data/final_corrected_dataset_with_aht_ast.csv'
logging.info(f"Saving the final dataset to {output_file}...")
ccasr.to_csv(output_file, index=False)
logging.info("Process completed successfully.")