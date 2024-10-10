import pandas as pd
import os
from datetime import datetime
from tabulate import tabulate

# Load the dataset
df = pd.read_csv('output/processed_dataset_with_ext.csv')

# Ensure agent_id_x is treated as string
df['agent_id_x'] = df['agent_id_x'].astype(str)

# Function to get the summary report
def get_summary(agent_id=None):
    # Filter data if agent_id is provided
    if agent_id:
        agent_data = df[df['agent_id_x'] == str(agent_id)]
        if agent_data.empty:
            print(f"No data found for agent_id: {agent_id}")
            return
    else:
        agent_data = df

    # Group data by agent_id_x and reason_label, with aggregations
    summary = agent_data.groupby(['agent_id_x', 'reason_label']).agg(
        num_calls=('reason_label', 'size'),
        avg_aht=('aht', 'mean'),
        avg_ast=('ast', 'mean'),
        avg_sentiment=('average_sentiment', 'mean'),
        avg_silence=('silence_percent_average', 'mean'),
        refund_offers=('refund_offer', lambda x: (x == 'Refund offered').sum()),
        voucher_offers=('voucher_offer', lambda x: (x == 'Voucher offered').sum()),
        skymiles_offers=('sky_miles_offer', lambda x: (x == 'SkyMiles offered').sum())
    ).reset_index()

    # Round for better readability
    summary['avg_aht'] = summary['avg_aht'].round(2)
    summary['avg_ast'] = summary['avg_ast'].round(2)
    summary['avg_sentiment'] = summary['avg_sentiment'].round(2)
    summary['avg_silence'] = summary['avg_silence'].round(2)

    if agent_id:
        # Print the summary for the agent to the console in a nice table format
        print(f"\nSummary for agent_id: {agent_id}")
        print(tabulate(summary, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        # Generate a CSV report for all agents
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'output/agent_report_{timestamp}.csv'
        os.makedirs('output', exist_ok=True)
        summary.to_csv(output_file, index=False)

        print(f"\nCSV report generated and saved to: {output_file}")


# Ask for agent_id or generate a full report
agent_id_input = input("Enter the agent_id (or press Enter to generate a full report for all agents): ")

# Generate the report based on user input
if agent_id_input:
    get_summary(agent_id_input)
else:
    get_summary()
