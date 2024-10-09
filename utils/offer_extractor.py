import re

def extract_offers(agent_solution, reason_label):
    agent_solution = agent_solution.lower()

    # Default values for each column
    refund_offer = "Refund not offered"
    voucher_offer = "Voucher not offered"
    voucher_value = "N/A"
    sky_miles_offer = "SkyMiles not offered"
    sky_miles_value = "N/A"
    change_fee_offer = "Change fee not charged"
    change_fee_value = "N/A"

    # Check if the reason label is one of the valid categories
    if reason_label in ['Delayed Flight', 'Missed Connecting Flight', 'Complaint', 'Miscellaneous Issue', 'Cancelled', 'Baggage Mishandling', 'Change Flight', 'Get Details', 'Cancelled Flight']:
        # Define regex patterns for full refund and no refund
        full_refund_patterns = [
            r"happy to provide you with a full refund",
            r"happy to process that full refund",
            r"go ahead and process that full refund",
            r"happy to process a full refund",
            r"let me offer you a full refund",
            r"can offer you a full refund",
            r"processed a full refund",
            r"full refund is certainly justified",
            r"go ahead and refund",
            r"I can offer in compensation is a full refund"
        ]

        no_refund_patterns = [
            r"unfortunately",
            r"non-refundable",
            r"unable to provide a full refund",
            r"not able to offer a refund",
            r"can't offer"
        ]

        # Check if any of the full refund patterns match
        for pattern in full_refund_patterns:
            if re.search(pattern, agent_solution):
                refund_offer = "Refund offered"
                break

        # Check if no refund was given
        if refund_offer == "Refund not offered":
            for pattern in no_refund_patterns:
                if re.search(pattern, agent_solution):
                    refund_offer = "Refund not offered"
                    break

        # Check for travel voucher or credit and extract the value if present
        if 'voucher' in agent_solution or 'credit' in agent_solution or 'offer' in agent_solution:
            voucher_offer = "Voucher offered"
            # Look for multiple values with a $ sign before "voucher" or "credit", allowing for commas in the number
            voucher_matches = re.findall(r'\$(\d{1,3}(?:,\d{3})*)', agent_solution)
            if voucher_matches:
                # Use the value found later in the text and remove commas
                voucher_value = f"{voucher_matches[-1].replace(',', '')}$"
            else:
                voucher_value = "N/A"

        # Check for SkyMiles bonus by finding a number (with or without commas) preceding "bonus" or "sky miles"
        bonus_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(bonus|sky miles)', agent_solution)
        if bonus_match:
            sky_miles_value = bonus_match.group(1).replace(',', '')  # Clean up any commas in the SkyMiles value
            if sky_miles_value == "000":
                sky_miles_value = "N/A"  # Handle cases where invalid SkyMiles values are found
            else:
                sky_miles_offer = "SkyMiles offered"
                sky_miles_value = f"{sky_miles_value} SkyMiles"
    
    # Check for change fee information if the reason label is 'Change Flight'
    # Check for change fee information if the reason label is 'Change Flight'
    if reason_label == 'Change Flight':
        # List of regex patterns indicating a waived change fee
        waived_change_fee_patterns = [
            r'waive(d)? the change fee',
            r'remove(d)? the extra fee',
            r'cancel(l)? the change fee',
            r'no change fee will apply',
            r'we will cover the change fee',
            r'can waive'
        ]

        # Check if any of the waived change fee patterns match
        for pattern in waived_change_fee_patterns:
            if re.search(pattern, agent_solution):
                change_fee_offer = "Change fee waived"
                break

        if change_fee_offer == "Change fee not charged":
            # List of regex patterns indicating a change fee charge
            charged_change_fee_patterns = [
                r'additional (\d{1,3}(?:,\d{3})*)\$',  # Match "$ amount additional fee"
                r'\$(\d{1,3}(?:,\d{3})*) change fee',   # Match "$ amount change fee"
                r'change fee of \$(\d{1,3}(?:,\d{3})*)',  # Match "change fee of $xx"
                r'\$(\d{1,3}(?:,\d{3})*) fee',  # Match "$xx fee"
                r'\$(\d{1,3}(?:,\d{3})*) is pretty steep',  # Match "$xx is pretty steep"
                r'\$(\d{1,3}(?:,\d{3})*) more',  # Match "$xx more"
                r'\$(\d{1,3}(?:,\d{3})*) difference',  # Match "$xx difference"
                r'\$(\d{1,3}(?:,\d{3})*) higher'  # Match "$xx higher"
            ]

            # Check for charged change fee and capture value
            for pattern in charged_change_fee_patterns:
                change_fee_match = re.search(pattern, agent_solution)
                if change_fee_match:
                    change_fee_offer = "Change fee charged"
                    change_fee_value = f"{change_fee_match.group(1).replace(',', '')}$"
                    break

    # Return structured information as a dictionary
    return {
        'refund_offer': refund_offer,
        'voucher_offer': voucher_offer,
        'voucher_value': voucher_value,
        'sky_miles_offer': sky_miles_offer,
        'sky_miles_value': sky_miles_value,
        'change_fee_offer': change_fee_offer,
        'change_fee_value': change_fee_value
    }