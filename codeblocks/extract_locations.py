import pandas as pd

# Read the merged dataset
df = pd.read_csv('corrected_dataset.csv')

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
        from_city = ' '.join(words_between)
        
        # Extract words after "to"
        words_after_to = lower_transcript[to_index + 4:].strip().split()
        
        # Remove unwanted words after the "to" keyword and limit words
        unwanted_words = ['next', 'for', 'was', 'is', 'will']
        to_city_words = []
        for word in words_after_to:
            if word in unwanted_words:
                break
            # If the word ends with '.', remove '.' and stop adding further words
            if word.endswith('.'):
                to_city_words.append(word.rstrip('.'))
                break
            to_city_words.append(word)
            
            # Stop if we already have 2 words
            if len(to_city_words) >= 2:
                break
        
        # Join and clean the "to" city
        to_city = ' '.join(to_city_words).strip()

        return from_city, to_city

# Apply the function to the conversation column and create new columns
df[['travelling_from', 'travelling_to']] = df['call_transcript'].apply(
    lambda x: pd.Series(extract_first_city_pair(x))
)

# Save the updated DataFrame with the new columns
df.to_csv('corrected_dataset_with_travel_info.csv', index=False)