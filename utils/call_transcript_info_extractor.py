import logging

def extract_info(transcript):
    call_reason = []
    agent_solutions = []
    customer_responses = []

    lines = transcript.split('\n')
    capturing_reason = False
    capturing_solutions = False
    capture_more_customer_lines = False

    customer_line_count = 0

    for line in lines:
        if "Customer" in line and "I'm calling" in line:
            capturing_reason = True
            reason_part = line.split("I'm calling")[-1].strip()
            call_reason.append(reason_part)
            if "about" in reason_part or "regarding" in reason_part:
                capture_more_customer_lines = True

        if capture_more_customer_lines and "Customer" in line:
            if customer_line_count < 2:
                call_reason.append(line.strip())
                customer_line_count += 1
            else:
                capture_more_customer_lines = False

        if "Agent" in line and capturing_reason:
            capturing_reason = False

        if capturing_reason:
            call_reason.append(line.strip())

        if "Agent" in line:
            capturing_solutions = True
            agent_solutions.append("Let me " + line)

        if "Customer" in line:
            capturing_solutions = False
            customer_responses.append(line.strip())

    call_reason = " | ".join(call_reason[:2]) if call_reason else "No specific call reason"
    customer_accepted = customer_responses[-2] if len(customer_responses) >= 2 else customer_responses[0] if len(customer_responses) == 1 else "No customer response found"
    formatted_solutions = [f"Solution {i+1}: {sol}" for i, sol in enumerate(agent_solutions)]

    return {
        "actual_call_reason": call_reason,
        "agent_solutions": " | ".join(formatted_solutions),
        "customer_accepted": customer_accepted
    }