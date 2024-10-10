# Project Setup and Execution Guide

This guide provides step-by-step instructions for setting up and running the project. Follow these steps to ensure the correct setup and execution of the analysis scripts.

## Directory Structure

Ensure that your project directory is organized as follows:

project_root/
├── data/
│   ├── calls.csv
│   ├── customers.csv
│   ├── info.md
│   ├── reason.csv
│   ├── sentiment.csv
│   └── test.csv
├── output/
│   └── (generated output will be stored here)
├── get_details_metrics.py
├── main.py
├── analysis.py
├── requirements.txt
└── run.md

## Prerequisites

Ensure you have **Python 3** installed on your system. You can verify this by running:

python3 --version

Ensure that you have made the /data and /output folders in the root dir and inside data folder put all the raw csv dataset files just like how it is specified in the Directory Structure.

### 1. Virtual Environment Setup

Create a virtual environment in the root directory to manage project dependencies:

python3 -m venv venv

### 2. Activate the Virtual Environment

Activate the virtual environment depending on your operating system:

- **Windows**:
  venv\Scripts\activate

- **Linux/Mac**:
  source venv/bin/activate

### 3. Install Required Dependencies

Once the virtual environment is activated, install the required packages by running:

pip3 install -r requirements.txt

## Running the Project

### 1. Execute the Main Script

You can run either of the two Python scripts, depending on your specific requirements:

- To run the main analysis script:

  python3 main.py

- Alternatively, you can run the analysis script for detailed insights:

  python3 analysis.py

These scripts will process the datasets and generate output in the `output/` directory.

### 2. Run IVR Recommendations

To print the IVR recommendation details, run the `get_details_metrics.py` script after the analysis:

python3 get_details_metrics.py

This will display the metrics and recommendations based on the IVR data.

### 2. Run agent Report Generator

To retrieve and analyze agent performance metrics, use the get_details_metrics.py script. This script calculates and presents key performance indicators (KPIs) that are vital for assessing agent efficiency and effectiveness. The metrics include:

Average Handle Time (AHT): The average duration spent by an agent on a call, including hold time and talk time.
Average Speed of Answer (ASA): The average time taken for a customer call to be answered by an agent.
Call Resolution Rate: The percentage of calls resolved during the first interaction with the customer.
Customer Satisfaction Score (CSAT): A measure of customer satisfaction based on feedback collected after the call.

How to Run
Ensure that you have already executed either main.py or analysis.py to process the data.

Run the metrics script using:

python3 get_details_metrics.py

You will be prompted to enter the agent ID for which you want to view metrics or press Enter to generate a full report of all agents.

The output will provide a detailed report of the agent performance metrics, allowing you to assess and improve overall customer service effectiveness.
