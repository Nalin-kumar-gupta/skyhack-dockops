import numpy as np
import pandas as pd
import logging
import spacy
import os
import re

# Setting up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Start the process and log the initialization
logging.info("Process started, initializing the spaCy model and reading files.")

# Load spaCy's English model
logging.info("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
logging.info("SpaCy model loaded successfully.")

# Step 1: Read CSV Files
logging.info("Reading CSV files...")
calls = pd.read_csv('data/calls.csv')
customers = pd.read_csv('data/customers.csv')
reasons = pd.read_csv('data/reason.csv')
sentiments = pd.read_csv('data/sentiment.csv')

logging.debug(f"Calls data shape: {calls.shape}, Sample:\n{calls.head()}")
logging.debug(f"Customers data shape: {customers.shape}, Sample:\n{customers.head()}")
logging.debug(f"Reasons data shape: {reasons.shape}, Sample:\n{reasons.head()}")
logging.debug(f"Sentiments data shape: {sentiments.shape}, Sample:\n{sentiments.head()}")

# Step 2: Merge Calls and Sentiments
logging.info("Merging 'calls' with 'sentiments' on 'call_id'...")
cas = pd.merge(calls, sentiments, on='call_id', how='left')
logging.debug(f"After merging 'calls' and 'sentiments', shape: {cas.shape}, Null counts:\n{cas.isnull().sum()}")

# Step 3: Merge with Reasons
logging.info("Merging 'cas' with 'reasons' on 'call_id'...")
casr = pd.merge(cas, reasons, on='call_id', how='left')
logging.debug(f"After merging 'cas' with 'reasons', shape: {casr.shape}, Null counts:\n{casr.isnull().sum()}")

# Step 4: Merge with Customers
logging.info("Merging 'casr' with 'customers' on 'customer_id'...")
ccasr = pd.merge(casr, customers, on='customer_id', how='left')
logging.debug(f"After merging 'casr' with 'customers', shape: {ccasr.shape}, Null counts:\n{ccasr.isnull().sum()}")

# Step 5: Data Cleaning on 'primary_call_reason'
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

# Step 6: Extract 'travelling_from' and 'travelling_to' from 'call_transcript'
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
            # logging.debug(f"Too many words between 'from' and 'to': {words_between}. Searching next...")
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
logging.debug(f"Sample of extracted locations: \n{ccasr[['travelling_from', 'travelling_to']].head()}")

# Step 7: Correct 'travelling_from' and 'travelling_to' using spaCy for validation
def extract_location(text):
    if pd.isna(text):  # Handle NaN cases
        return ""
    
    doc = nlp(text)
    
    # Extract GPE (Geopolitical Entity) from the text
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    
    return ""

logging.info("Correcting 'travelling_from' and 'travelling_to' locations using spaCy...")
ccasr['travelling_from'] = ccasr['travelling_from'].apply(lambda x: extract_location(x))
ccasr['travelling_to'] = ccasr['travelling_to'].apply(lambda x: extract_location(x))
logging.debug(f"Corrected locations: \n{ccasr[['travelling_from', 'travelling_to']].head()}")

# Step 8: Extract call reason, agent solutions, and customer response from transcripts
def extract_info(transcript):
    logging.debug(f"Extracting call reason and solutions from transcript: {transcript[:50]}")
    call_reason = []
    agent_solutions = []
    customer_responses = []

    lines = transcript.split('\n')
    capturing_reason = False
    capturing_solutions = False
    capture_more_customer_lines = False  # Flag to capture extra customer lines
    
    customer_line_count = 0  # Counter for capturing the first two customer lines
    
    for line in lines:
        # Extracting call reason when customer says "I'm calling"
        if "Customer" in line and "I'm calling" in line:
            capturing_reason = True
            reason_part = line.split("I'm calling")[-1].strip()
            call_reason.append(reason_part)  # append to the list
            
            # Check if "about" or "regarding" is mentioned in the reason
            if "about" in reason_part or "regarding" in reason_part:
                capture_more_customer_lines = True  # Trigger capturing more customer lines
        
        # Capture first two customer lines after "about" or "regarding"
        if capture_more_customer_lines and "Customer" in line:
            if customer_line_count < 2:  # Capture the first two customer lines
                call_reason.append(line.strip())
                customer_line_count += 1
            else:
                capture_more_customer_lines = False  # Stop after capturing 2 lines
        
        # Stopping the capture of the call reason when agent speaks
        if "Agent" in line and capturing_reason:
            capturing_reason = False
        
        # If still capturing the reason, append the lines
        if capturing_reason:
            call_reason.append(line.strip())  # appending to the list
        
        # Capturing solutions provided by agent
        if "Agent" in line:
            capturing_solutions = True
           
            agent_solutions.append("Let me " + line)
        
        # Stop capturing solutions when the customer responds
        if "Customer" in line:
            capturing_solutions = False
            customer_responses.append(line.strip())

    # If "about" or "regarding" was mentioned, add "about" to the start of the call reason
    if "about" in " ".join(call_reason).lower() or "regarding" in " ".join(call_reason).lower():
        call_reason = "about " + " | ".join(call_reason)
    else:
        # Only keep the first two customer lines if no special case was triggered
        call_reason = " | ".join(call_reason[:2]) if call_reason else ""

    # If the call_reason is still empty, capture the first two customer lines
    if not call_reason:
        customer_dialogue_lines = [line for line in lines if "Customer" in line][:2]  # Capture first two customer lines
        call_reason = " | ".join(customer_dialogue_lines) if customer_dialogue_lines else "No specific call reason"
    
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
logging.debug(f"Extracted call reasons and solutions: \n{extracted_df.head()}")
ccasr = pd.concat([ccasr, extracted_df], axis=1)

# Step 9: Categorize call reason
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
        elif 'cancelled' in call_reason:
            return 'Cancelled Flight'
        elif 'bag' in call_reason or 'baggage' in call_reason:
            return 'Baggage Mishandling'
        elif 'complain' in call_reason or 'not happy' in call_reason or 'complaint' in call_reason:
            return 'Complaint'
        else:
            return 'Get Details'
    elif call_reason.startswith("because") or call_reason.startswith("cause"):
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' in call_reason and ('missed' in call_reason or 'miss' in call_reason):
                return 'Missed Connecting Flight'
            else:
                return 'Delayed Flight'
        elif 'cancelled' in call_reason:
            return 'Cancelled Flight'
        elif 'bag' in call_reason or 'baggage' in call_reason:
            return 'Baggage Mishandling'
        else:
            if 'complain' in call_reason or 'complaint' in call_reason:
                return 'Complaint'
            else:
                return 'Miscellaneous Issue'
    
    else:
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' in call_reason and ('missed' in call_reason or 'miss' in call_reason):
                return 'Missed Connecting Flight'
            else:
                return 'Delayed Flight'
        elif 'cancelled' in call_reason:
            return 'Cancelled Flight'
        elif 'bag' in call_reason or 'baggage' in call_reason:
            return 'Baggage Mishandling'
        else:
            if 'complain' in call_reason or 'complaint' in call_reason:
                return 'Complaint'
            else:
                return 'Miscellaneous Issue'

logging.info("Categorizing based on 'actual_call_reason'...")
ccasr['reason_label'] = ccasr['actual_call_reason'].apply(categorize_reason)

# Step 10: Calculate AHT, AST, and extract Call Date
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



# Step 11: Function to extract structured offers based on agent solutions for 'Delayed Flights' and other categories
def extract_offers(agent_solution, reason_label):
    agent_solution = agent_solution.lower()

    # Default values for each column
    refund_offer = "Refund not offered"
    voucher_offer = "Voucher not offered"
    voucher_value = "N/A"
    sky_miles_offer = "SkyMiles not offered"
    sky_miles_value = "N/A"
    change_fee_offer = "Change fee not charged"
    change_fee_value = "N/A"

    # Check if the reason label is one of the valid categories
    if reason_label in ['Delayed Flight', 'Missed Connecting Flight', 'Complaint', 'Miscellaneous Issue', 'Cancelled', 'Baggage Mishandling', 'Change Flight', 'Get Details', 'Cancelled Flight']:
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
                refund_offer = "Refund offered"
                break

        # Check if no refund was given
        if refund_offer == "Refund not offered":
            for pattern in no_refund_patterns:
                if re.search(pattern, agent_solution):
                    refund_offer = "Refund not offered"
                    break

        # Check for travel voucher or credit and extract the value if present
        if 'voucher' in agent_solution or 'credit' in agent_solution or 'offer' in agent_solution:
            voucher_offer = "Voucher offered"
            # Look for multiple values with a $ sign before "voucher" or "credit", allowing for commas in the number
            voucher_matches = re.findall(r'\$(\d{1,3}(?:,\d{3})*)', agent_solution)
            if voucher_matches:
                # Use the value found later in the text and remove commas
                voucher_value = f"{voucher_matches[-1].replace(',', '')}$"
            else:
                voucher_value = "N/A"

        # Check for SkyMiles bonus by finding a number (with or without commas) preceding "bonus" or "sky miles"
        bonus_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(bonus|sky miles)', agent_solution)
        if bonus_match:
            sky_miles_value = bonus_match.group(1).replace(',', '')  # Clean up any commas in the SkyMiles value
            if sky_miles_value == "000":
                sky_miles_value = "N/A"  # Handle cases where invalid SkyMiles values are found
            else:
                sky_miles_offer = "SkyMiles offered"
                sky_miles_value = f"{sky_miles_value} SkyMiles"
    
    # Check for change fee information if the reason label is 'Change Flight'
    # Check for change fee information if the reason label is 'Change Flight'
    if reason_label == 'Change Flight':
        # List of regex patterns indicating a waived change fee
        waived_change_fee_patterns = [
            r'waive(d)? the change fee',
            r'remove(d)? the extra fee',
            r'cancel(l)? the change fee',
            r'no change fee will apply',
            r'we will cover the change fee',
            r'can waive'
        ]

        # Check if any of the waived change fee patterns match
        for pattern in waived_change_fee_patterns:
            if re.search(pattern, agent_solution):
                change_fee_offer = "Change fee waived"
                break

        if change_fee_offer == "Change fee not charged":
            # List of regex patterns indicating a change fee charge
            charged_change_fee_patterns = [
                r'additional (\d{1,3}(?:,\d{3})*)\$',  # Match "$ amount additional fee"
                r'\$(\d{1,3}(?:,\d{3})*) change fee',   # Match "$ amount change fee"
                r'change fee of \$(\d{1,3}(?:,\d{3})*)',  # Match "change fee of $xx"
                r'\$(\d{1,3}(?:,\d{3})*) fee',  # Match "$xx fee"
                r'\$(\d{1,3}(?:,\d{3})*) is pretty steep',  # Match "$xx is pretty steep"
                r'\$(\d{1,3}(?:,\d{3})*) more',  # Match "$xx more"
                r'\$(\d{1,3}(?:,\d{3})*) difference',  # Match "$xx difference"
                r'\$(\d{1,3}(?:,\d{3})*) higher'  # Match "$xx higher"
            ]

            # Check for charged change fee and capture value
            for pattern in charged_change_fee_patterns:
                change_fee_match = re.search(pattern, agent_solution)
                if change_fee_match:
                    change_fee_offer = "Change fee charged"
                    change_fee_value = f"{change_fee_match.group(1).replace(',', '')}$"
                    break

    # Return structured information as a dictionary
    return {
        'refund_offer': refund_offer,
        'voucher_offer': voucher_offer,
        'voucher_value': voucher_value,
        'sky_miles_offer': sky_miles_offer,
        'sky_miles_value': sky_miles_value,
        'change_fee_offer': change_fee_offer,
        'change_fee_value': change_fee_value
    }

# Example usage:
agent_solution = "We can offer you a full refund, a $100 travel voucher, and the $15,020 change fee."
reason_label = "Change Flight"
print(extract_offers(agent_solution, reason_label))

# Apply the extraction logic to the 'agent_solutions' column with the reason_label passed into the function
logging.info("Extracting structured offers from 'agent_solutions' for Irregular Operations")

# Apply the extract_offers function and expand the resulting dictionary into separate columns
offer_columns = ccasr.apply(
    lambda row: pd.Series(extract_offers(row['agent_solutions'], row['reason_label'])),
    axis=1
)

# Merge the new columns back into the main DataFrame
ccasr = pd.concat([ccasr, offer_columns], axis=1)

# Display the updated DataFrame
print(ccasr[['refund_offer', 'voucher_offer', 'voucher_value', 'sky_miles_offer', 'sky_miles_value']].head())


# Step 12: Save Final Dataset
output_file = 'output/processed_dataset_with_ext.csv'
logging.info(f"Saving the final dataset to {output_file}...")
ccasr.to_csv(output_file, index=False)
logging.info("Process completed successfully.")