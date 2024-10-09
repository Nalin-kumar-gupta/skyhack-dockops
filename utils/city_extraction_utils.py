import pandas as pd

def extract_first_city_pair(transcript):
    lower_transcript = str(transcript).lower()

    search_index = 0
    while True:
        from_index = lower_transcript.find('from ', search_index)
        if from_index == -1:
            return None, None

        to_index = lower_transcript.find(' to ', from_index)
        if to_index == -1:
            return None, None
        
        words_between = lower_transcript[from_index + 5:to_index].strip().split()
        if len(words_between) > 4:
            search_index = to_index + 4
            continue

        from_city = ' '.join(words_between).title()
        words_after_to = lower_transcript[to_index + 4:].strip().split()
        to_city_words = [word for word in words_after_to if word.isalpha()][:2]

        to_city = ' '.join(to_city_words).strip().title()

        if to_city.lower() == 'la':
            to_city = 'Los Angeles'
        if from_city.lower() == 'la':
            from_city = 'Los Angeles'
        if to_city.lower() == 'nyc':
            to_city = 'New York'
        if from_city.lower() == 'nyc':
            from_city = 'New York'
            
        return from_city, to_city
    

def extract_location(text, nlp):
    if pd.isna(text):  # Handle NaN cases
        return ""
    
    doc = nlp(text)
    
    # Extract GPE (Geopolitical Entity) from the text
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    
    return ""