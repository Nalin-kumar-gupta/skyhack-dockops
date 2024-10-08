import pandas as pd
import spacy

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Function to extract location using spaCy
def extract_location(text):
    if pd.isna(text):  # Handle NaN cases
        return ""
    
    # Process the text using spaCy
    doc = nlp(text)
    
    # Extract GPE (Geopolitical Entity) from the text
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    
    # If no GPE found, return empty string
    return ""

# Read the transcript data from CSV file
input_file_path = 'corrected_dataset_with_info.csv'  # Replace with your actual file path
df = pd.read_csv(input_file_path)

# Apply spaCy to extract locations for 'travelling_from' and 'travelling_to'
df['travelling_from'] = df['travelling_from'].apply(lambda x: extract_location(x))
df['travelling_to'] = df['travelling_to'].apply(lambda x: extract_location(x))

# Write the updated DataFrame to a new CSV file
output_file_path = 'corrected_dataset_with_valid_locations.csv'  # Replace with your desired output file path
df.to_csv(output_file_path, index=False)

# Inform the user that the file has been created
print(f"The updated CSV file with spaCy-extracted locations has been saved at {output_file_path}.")