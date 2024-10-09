import pandas as pd
import re
from tabulate import tabulate

# Load data from CSV
df = pd.read_csv('output/processed_dataset_with_ext.csv')

# Check the content of 'reason_label' column to confirm available categories
print("Unique values in 'reason_label':", df['reason_label'].unique())

# Define the keywords for each metric
metrics = {
    'Wants Reminder': ['remind', 'reminder', 'notify', 'notification'],
    'Wants to Check Baggage Limit': ['bag', 'limit', 'weight', 'baggage', 'luggage', 'carry-on'],
    'Wants to Check Flight Schedule': ['double check', 'flight time', 'schedule', 'departure time', 'status', 'arrival time', 'boarding time'],
    'Concerned About Delays or Cancellations': ['weather', 'forecast', 'delays', 'delay', 'delayed', 'cancellations', 'canceled', 'concerned', 'storm', 'reschedule'],
    'Wants To Get Refund': ['refund', 'compensation', 'reimbursement'],
    'Wants to Upgrade Seat': ['upgrade', 'seat change', 'first class', 'business class', 'premium', 'better seat']
}

# Sample: Extract 'Get Details' customer dialogues
def extract_get_details_concern(call_transcript):
    lines = call_transcript.split('\n')
    customer_dialogues = []
    
    # Iterate over the lines to find "Agent:" with a question mark and capture following "Customer:" lines
    for i, line in enumerate(lines):
        if re.search(r'Agent:.*\?', line):
            # Look ahead in the next few lines for the "Customer:" response(s)
            for j in range(i + 1, min(i + 4, len(lines))):  # Check up to 3 lines after the agent's question
                if "Customer:" in lines[j]:
                    customer_dialogue = lines[j].split("Customer:")[-1].strip()
                    customer_dialogues.append(customer_dialogue)  # Append the customer response

    # Combine all customer responses into one string, if multiple responses are found
    combined_dialogue = ' '.join(customer_dialogues) if customer_dialogues else None
    return combined_dialogue

# Analyze each dialogue for the defined metrics
def analyze_concerns(dialogue):
    analysis = {}
    if dialogue:
        for metric, keywords in metrics.items():
            found = any(re.search(r'\b' + keyword + r'\b', dialogue, re.IGNORECASE) for keyword in keywords)
            analysis[metric] = found
    else:
        for metric in metrics.keys():
            analysis[metric] = False
    return analysis

# Initialize a dictionary to count occurrences of each concern
concern_counts = {metric: 0 for metric in metrics.keys()}

# Process each entry where the 'reason_label' is 'Get Details'
for index, row in df[df['reason_label'] == 'Get Details'].iterrows():
    call_transcript = row['call_transcript']
    customer_dialogue = extract_get_details_concern(call_transcript)
    
    # Analyze the extracted dialogue and update the concern counts
    if customer_dialogue:
        concerns_analysis = analyze_concerns(customer_dialogue)
        for metric, result in concerns_analysis.items():
            if result:
                concern_counts[metric] += 1

# Convert the concern counts to a DataFrame for better visualization
concern_counts_df = pd.DataFrame(list(concern_counts.items()), columns=['Concern', 'Frequency'])

# Display the table beautifully on the console using tabulate
print(tabulate(concern_counts_df, headers='keys', tablefmt='fancy_grid', showindex=False))
