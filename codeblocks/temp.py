import pandas as pd

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

# Function to validate locations
def validate_location(row, column_name, valid_list):
    # Check if the value in the column matches a valid city name
    if pd.notna(row[column_name]) and row[column_name].lower() in valid_list:
        return row[column_name]  # Keep the valid entry
    else:
        return ''  # Empty the cell if not valid

# Read the transcript data from CSV file
input_file_path = 'corrected_dataset_with_info.csv'  # Replace with your actual file path
df = pd.read_csv(input_file_path)

# Validate 'from' and 'to' locations
df['from_city'] = df.apply(lambda row: validate_location(row, 'from_city', from_city_common_names), axis=1)
df['to_city'] = df.apply(lambda row: validate_location(row, 'to_city', to_city_common_names), axis=1)

# Write the updated DataFrame to a new CSV file
output_file_path = 'corrected_dataset_with_valid_locations.csv'  # Replace with your desired output file path
df.to_csv(output_file_path, index=False)

# Inform the user that the file has been created
print(f"The updated CSV file with validated locations has been saved at {output_file_path}.")