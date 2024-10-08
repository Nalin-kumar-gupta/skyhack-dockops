import pandas as pd

# Function to extract call reason, solution provided by the agent, and accepted solution
def extract_info(transcript):
    call_reason = []
    agent_solution = []
    customer_response = []

    # Splitting transcript into sentences
    lines = transcript.split('\n')
    
    for line in lines:
        # Check for "I'm calling" pattern for call reason
        if "Customer" in line and "I'm calling" in line:
            # Extract the part after "I'm calling" and before the first full stop
            reason_part = line.split("I'm calling")[-1].split('.')[0].strip()
            call_reason.append(reason_part)
        
        # For the agent's solution, using a simple rule
        if "Agent" in line:
            if "I can" in line or "offer" in line or "waive" in line:
                # Extract the full line as the agent's solution
                agent_solution.append(line.strip())
        
        # For the customer's acceptance
        if "Customer" in line:
            if "Yes" in line or "that works" in line or "thank you" in line:
                # Extract the full line as customer acceptance
                customer_response.append(line.strip())

    # Join multiple matches
    return {
        "Call Reason": " | ".join(call_reason),
        "Agent Solution": " | ".join(agent_solution),
        "Customer Accepted": " | ".join(customer_response)
    }

# Read the transcript data from CSV file
input_file_path = 'corrected_dataset_w.csv'  # Replace with your actual file path
df = pd.read_csv(input_file_path)

# Assuming the column name containing the call transcripts is 'Transcript'
# Apply extraction function to each transcript
df_extracted = df['Transcript'].apply(extract_info)

# Convert the extracted data into a DataFrame
extracted_df = pd.DataFrame(list(df_extracted))

# Merge the extracted data with the original DataFrame
final_df = pd.concat([df, extracted_df], axis=1)

# Write the updated DataFrame to a new CSV file
output_file_path = 'corrected_dataset_with_info.csv'  # Replace with your desired output file path
final_df.to_csv(output_file_path, index=False)

# Inform the user that the file has been created
print(f"The updated CSV file has been saved at {output_file_path}.")