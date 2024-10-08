import pandas as pd

# Function to extract call reason, solutions provided by the agent, and accepted solution
def extract_info(transcript):
    call_reason = []
    agent_solutions = []
    customer_responses = []  # Store all customer responses

    # Splitting transcript into lines
    lines = transcript.split('\n')
    
    capturing_reason = False
    capturing_solutions = False
    
    for line in lines:
        # Check for "I'm calling" pattern for call reason and start capturing
        if "Customer" in line and "I'm calling" in line:
            capturing_reason = True
            # Extract the part after "I'm calling"
            reason_part = line.split("I'm calling")[-1].strip()
            call_reason.append(reason_part)
        
        # Stop capturing call reason when the agent starts speaking again
        if "Agent" in line and capturing_reason:
            capturing_reason = False
        
        # Continue capturing the call reason until the agent speaks
        if capturing_reason:
            call_reason.append(line.strip())
        
        # For the agent's solutions based on "Let me" pattern
        if "Agent" in line and "Let me" in line:
            capturing_solutions = True
            solution_part = line.split("Let me")[-1].strip()
            agent_solutions.append("Let me " + solution_part)
        
        # Stop capturing solutions when the customer speaks again
        if "Customer" in line:
            capturing_solutions = False
            # Store all customer responses
            customer_responses.append(line.strip())

    # Get the second-to-last customer response, if available
    if len(customer_responses) >= 2:
        customer_accepted = customer_responses[-2]
    elif len(customer_responses) == 1:
        customer_accepted = customer_responses[0]  # Fallback to the last response if only one exists
    else:
        customer_accepted = "No customer response found"

    # Join multiple solutions as Solution 1, Solution 2, etc.
    formatted_solutions = [f"Solution {i+1}: {sol}" for i, sol in enumerate(agent_solutions)]
    
    # Join multiple matches
    return {
        "Call Reason": " | ".join(call_reason),
        "Agent Solutions": " | ".join(formatted_solutions),
        "Customer Accepted": customer_accepted
    }

# Read the transcript data from CSV file
input_file_path = 'corrected_dataset_w.csv'  # Replace with your actual file path
df = pd.read_csv(input_file_path)

# Assuming the column name containing the call transcripts is 'Transcript'
# Apply extraction function to each transcript
df_extracted = df['call_transcript'].apply(extract_info)

# Convert the extracted data into a DataFrame
extracted_df = pd.DataFrame(list(df_extracted))

# Merge the extracted data with the original DataFrame
final_df = pd.concat([df, extracted_df], axis=1)

# Write the updated DataFrame to a new CSV file
output_file_path = 'corrected_dataset_with_info.csv'  # Replace with your desired output file path
final_df.to_csv(output_file_path, index=False)

# Inform the user that the file has been created
print(f"The updated CSV file has been saved at {output_file_path}.")