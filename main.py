import logging
import spacy
import pandas as pd
from utils.logger import setup_logging
from utils.data_loader import load_csv_data
from utils.dataframe_merger import merge_data
from utils.clean_primary_call_reason_cell import clean_primary_call_reason
from utils.city_extraction_utils import extract_first_city_pair, extract_location
from utils.call_transcript_info_extractor import extract_info
from utils.reason_labeler import categorize_reason
from utils.aht_ast_calculator import calculate_aht_ast
from utils.offer_extractor import extract_offers

# Step 1: Setup Logging
setup_logging()

# Step 2: Load Data
calls, customers, reasons, sentiments = load_csv_data()

# Step 3: Merge Dataframes
ccasr = merge_data(calls, sentiments, reasons, customers)

# Step 4: Clean 'primary_call_reason'
ccasr = clean_primary_call_reason(ccasr)

# Step 5: Extract 'travelling_from' and 'travelling_to' from 'call_transcript'
ccasr[['travelling_from', 'travelling_to']] = ccasr['call_transcript'].apply(
    lambda x: pd.Series(extract_first_city_pair(x))
)
logging.debug(f"Sample of extracted locations: \n{ccasr[['travelling_from', 'travelling_to']].head()}")

# Load spaCy's English model
logging.info("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
logging.info("SpaCy model loaded successfully.")


# Step 6: Correct the extracted location by matching them with gpe/ner
logging.info("Correcting 'travelling_from' and 'travelling_to' locations using spaCy...")
ccasr['travelling_from'] = ccasr['travelling_from'].apply(lambda x: extract_location(x, nlp))
ccasr['travelling_to'] = ccasr['travelling_to'].apply(lambda x: extract_location(x, nlp))
logging.debug(f"Corrected locations: \n{ccasr[['travelling_from', 'travelling_to']].head()}")


# Step 7: Extract call reason, solutions, and customer responses from transcripts
logging.info("Extracting call reason, solutions, and customer responses from transcripts...")
df_extracted = ccasr['call_transcript'].apply(extract_info)
extracted_df = pd.DataFrame(list(df_extracted))
logging.debug(f"Extracted call reasons and solutions: \n{extracted_df.head()}")
ccasr = pd.concat([ccasr, extracted_df], axis=1)

# Step 8: Categorize call reason
logging.info("Categorizing based on 'actual_call_reason'...")
ccasr['reason_label'] = ccasr['actual_call_reason'].apply(categorize_reason)

# Step 9: Calculate AHT, AST, and extract Call Date
logging.info("Calculating AHT, AST, and extracting 'call_date'...")
ccasr = calculate_aht_ast(ccasr)

# Step 10: Extract structured offers based on agent solutions for different categories
logging.info("Extracting structured offers from 'agent_solutions' for irregular operations...")
offer_columns = ccasr.apply(
    lambda row: pd.Series(extract_offers(row['agent_solutions'], row['reason_label'])),
    axis=1
)
ccasr = pd.concat([ccasr, offer_columns], axis=1)

# Step 11: Save the final dataset
output_file = 'output/processed_dataset_with_ext.csv'
logging.info(f"Saving the final dataset to {output_file}...")
ccasr.to_csv(output_file, index=False)
logging.info("Process completed successfully.")