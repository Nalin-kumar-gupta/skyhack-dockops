import pandas as pd
import re

# Read the merged dataset
df = pd.read_csv('corrected_dataset.csv')

# List of common city names
from_city_common_names = [
    "atlanta", "boston", "chicago", "colorado springs", "dallas", "delhi", 
    "denver", "detroit", "ewr", "newark", "houston", "jfk", "la", "lax", 
    "los angeles", "london", "miami", "milwaukee", "minneapolis", "nashville", 
    "new york", "o'hare", "nyc", "orlando", "phoenix", "raleigh", 
    "sacramento", "san fran", "san francisco", "seattle", "sfo", "xyz"
]

to_city_common_names = [
    "atlanta", "boston", "barcelona", "buffalo", "chicago", "cleveland", 
    "dallas", "delhi", "denver", "detroit", "dubai", "dublin", "ewr", 
    "newark", "hawaii", "honolulu", "houston", "jfk", "la", "lax", 
    "los angeles", "laguardia", "las vegas", "heathrow", "lhr", "london", 
    "miami", "milwaukee", "minneapolis", "madrid", "mumbai", "new orleans", 
    "nashville", "new york", "o'hare", "nyc", "orlando", "phoenix", 
    "paris", "phl", "portland", "raleigh", "sacramento", "san fran", 
    "san francisco", "seattle", "sfo", "xyz", "rome", "san diego", 
    "sydney", "tampa"
]

# Unwanted words set
unwanted_words = [
    'next', 'for', 'was', 'is', 'will', 'tomorrow', 'and', 'scheduled', 
    'last', 'week', 'month', 'year', 'yesterday', 'today', 'day', 'then', 
    'later', 'around', 'via', 'towards', 'approximately', 'arriving', 'departing', 
    'going', 'leaving', 'back', 'trip', 'meeting', 'visit', 'returning', 'morning', 
    'evening', 'afternoon', 'night', 'am', 'pm', 'that', 'agent', 'on'
]

# Function to extract the first city pair
def extract_first_city_pair(transcript):
    # Convert transcript to lowercase for case-insensitive search
    lower_transcript = str(transcript).lower()

    # Start searching from the beginning of the transcript
    search_index = 0
    
    while True:
        # Find the start of "from"
        from_index = lower_transcript.find('from ')
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
        from_city = ' '.join(words_between).title()
        from_city_lower = from_city.lower()  # Convert once to lowercase

        # Extract words after "to"
        words_after_to = lower_transcript[to_index + 4:].strip().split()

        # Clean and limit words for "to" city
        to_city_words = [re.sub(r'[^a-zA-Z\s]', '', word) for word in words_after_to if word.rstrip('.,') not in unwanted_words]
        to_city_words = [word for word in to_city_words if word]  # Remove empty strings

        # Limit to max 2 words
        to_city = ' '.join(to_city_words[:2]).title()
        to_city_lower = to_city.lower()

        # Special replacements for "la" and "nyc"
        if to_city_lower == 'la':
            to_city = 'Los Angeles'
        if from_city_lower == 'la':
            from_city = 'Los Angeles'
        if to_city_lower == 'nyc':
            to_city = 'New York'
        if from_city_lower == 'nyc':
            from_city = 'New York'

        # # Validate "from_city" against the list of common city names
        # for city_name in from_city_common_names:
        #     # Check if the city_name is a substring in from_city
        #     if city_name in from_city_lower:
        #         from_city = city_name.title()
        #         break

        # # Validate "to_city" against the list of common city names
        # for city_name in to_city_common_names:
        #     # Check if the city_name is a substring in to_city
        #     if city_name in to_city_lower:
        #         to_city = city_name.title()
        #         break

        return from_city, to_city

# Apply the function to the conversation column and create new columns
df[['travelling_from', 'travelling_to']] = df['call_transcript'].apply(
    lambda x: pd.Series(extract_first_city_pair(x))
)

# Save the updated DataFrame with the new columns
df.to_csv('corrected_dataset_with_travel_info.csv', index=False)