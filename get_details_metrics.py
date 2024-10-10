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

# Configuration to specify filtering based on 'travelling_from' and 'travelling_to'
config = {
    'filter_by_travel': True,  # Set to True if you want to apply the travel filter
    'travelling_from': 'Chicago',  # Specify the travelling_from value or leave empty for no filter
    'travelling_to': 'Los Angeles'  # Specify the travelling_to value or leave empty for no filter
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

# Initialize a dictionary to count occurrences and accumulate aht/ast for each concern
concern_stats = {metric: {'count': 0, 'aht_sum': 0, 'ast_sum': 0} for metric in metrics.keys()}

# Process each entry where the 'reason_label' is 'Get Details'
for index, row in df[df['reason_label'] == 'Get Details'].iterrows():
    
    # Apply travel filter if configured
    if config['filter_by_travel']:
        if not (
            (config['travelling_from'] == row['travelling_from'] if config['travelling_from'] else True) and
            (config['travelling_to'] == row['travelling_to'] if config['travelling_to'] else True)
        ):
            continue  # Skip this row if it doesn't match the travelling_from/to filter
    
    call_transcript = row['call_transcript']
    customer_dialogue = extract_get_details_concern(call_transcript)
    
    # Analyze the extracted dialogue and update the concern stats
    if customer_dialogue:
        concerns_analysis = analyze_concerns(customer_dialogue)
        for metric, result in concerns_analysis.items():
            if result:
                concern_stats[metric]['count'] += 1
                concern_stats[metric]['aht_sum'] += row['aht']  # Sum up aht
                concern_stats[metric]['ast_sum'] += row['ast']  # Sum up ast

# Prepare the data for tabulation (include average aht and ast calculations)
concern_data = []
for metric, stats in concern_stats.items():
    if stats['count'] > 0:
        avg_aht = stats['aht_sum'] / stats['count']
        avg_ast = stats['ast_sum'] / stats['count']
    else:
        avg_aht = avg_ast = 0  # Avoid division by zero

    concern_data.append([metric, stats['count'], round(avg_aht, 2), round(avg_ast, 2)])

# Convert the concern data to a DataFrame for better visualization
concern_data_df = pd.DataFrame(concern_data, columns=['Concern', 'Frequency', 'Average AHT (mins)', 'Average AST (mins)'])

# Display the table beautifully on the console using tabulate
print(tabulate(concern_data_df, headers='keys', tablefmt='fancy_grid', showindex=False))
