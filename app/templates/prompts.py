support_prompt_template = """
You are a helpful customer support assistant. 
The customer has the following issue: {ticket_description}

Previous messages:
{message_history}

Customer's latest message: {latest_message}

Provide a helpful response that addresses their concern:
"""