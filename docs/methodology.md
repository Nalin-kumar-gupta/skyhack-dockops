# Methodology

This document outlines the methodology used to process customer call data and extract meaningful insights.

## 1. Initialization and Setup
The process starts by importing necessary libraries such as `numpy`, `pandas`, `logging`, `spacy`, and `re`. Logging is configured to provide detailed debug information during the execution.

The spaCy English language model (`en_core_web_sm`) is loaded to process and validate textual data.

## 2. Reading CSV Files
We read multiple CSV files including `calls.csv`, `customers.csv`, `reason.csv`, and `sentiment.csv`. These files contain data regarding customer calls, their reasons, sentiments, and customer information. The data shapes and sample entries are logged for verification.

## 3. Data Merging
The data is merged step by step:
- **Calls** are merged with **Sentiments** based on the `call_id`.
- The result is further merged with **Reasons** and then with **Customers** using the `call_id` and `customer_id`.

## 4. Data Cleaning
The column `primary_call_reason` is cleaned by:
- Filling NaN values, converting to lowercase, and removing special characters.
- Removing stopwords and extra spaces, then replacing any remaining empty values with 'othertopics.'

## 5. Extracting Locations from Transcripts
We extract travel locations from the `call_transcript` column by identifying patterns like "from" and "to." These locations are further validated using spaCy to extract geopolitical entities (GPE).

## 6. Extracting Call Reason, Solutions, and Customer Responses
A custom function extracts call reasons, solutions provided by agents, and customer responses from the `call_transcript`. It identifies key patterns such as "I'm calling" or solutions offered by agents and stores them in structured columns.

## 7. Categorizing Call Reasons
The actual call reasons are categorized into predefined labels like 'Complaint,' 'Baggage Mishandling,' and 'Cancelled Flight,' based on keywords in the call reason text.

## 8. Calculating AHT, AST, and Call Dates
The Average Handle Time (AHT), Average Speed to Answer (AST), and `call_date` are calculated using timestamps from the dataset.

## 9. Structured Offer Extraction
A function extracts structured information such as refunds, vouchers, and SkyMiles offers from the agent's solutions, particularly for categories like 'Delayed Flight' and 'Change Flight.'

## 10. Final Dataset Export
The final processed dataset is saved as a CSV file in the `output/` directory, logging the success of the operation.
