import pandas as pd
def categorize_reason(call_reason):
    if pd.isna(call_reason) or call_reason.strip() == "":
        return 'Miscellaneous Issue'

    call_reason = call_reason.lower().strip()

    if call_reason.startswith("to complain"):
        return 'Complaint'
    elif call_reason.startswith("to inquire"):
        return 'Get Details'
    elif call_reason.startswith("about") or call_reason.startswith("regarding"):
        if 'wanted to' in call_reason and 'check' in call_reason:
            return 'Get Details'
        elif 'change' in call_reason:
            return 'Change Flight'
        elif 'cancelled' in call_reason:
            return 'Cancelled Flight'
        elif 'bag' in call_reason or 'baggage' in call_reason:
            return 'Baggage Mishandling'
        elif 'complain' in call_reason or 'not happy' in call_reason or 'complaint' in call_reason:
            return 'Complaint'
        else:
            return 'Get Details'
    elif call_reason.startswith("because") or call_reason.startswith("cause"):
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' in call_reason and ('missed' in call_reason or 'miss' in call_reason):
                return 'Missed Connecting Flight'
            else:
                return 'Delayed Flight'
        elif 'cancelled' in call_reason:
            return 'Cancelled Flight'
        elif 'bag' in call_reason or 'baggage' in call_reason:
            return 'Baggage Mishandling'
        else:
            if 'complain' in call_reason or 'complaint' in call_reason:
                return 'Complaint'
            else:
                return 'Miscellaneous Issue'
    
    else:
        if 'change' in call_reason:
            return 'Change Flight'
        elif 'delay' in call_reason or 'delayed' in call_reason:
            if 'connecting' in call_reason and ('missed' in call_reason or 'miss' in call_reason):
                return 'Missed Connecting Flight'
            else:
                return 'Delayed Flight'
        elif 'cancelled' in call_reason:
            return 'Cancelled Flight'
        elif 'bag' in call_reason or 'baggage' in call_reason:
            return 'Baggage Mishandling'
        else:
            if 'complain' in call_reason or 'complaint' in call_reason:
                return 'Complaint'
            else:
                return 'Miscellaneous Issue'