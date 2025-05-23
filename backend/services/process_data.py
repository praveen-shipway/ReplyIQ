import re
import spacy
from datetime import datetime, timedelta

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model for spaCy...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define intent categories and keywords
intent_keywords = {
    "wismo": ["where", "track", "status", "delivery", "arrival", "shipping"],
    "cancel": ["cancel", "cancelling", "void", "stop order", "remove"],
    "reschedule": ["update", "modify", "change", "reschedule", "adjust", "edit"],
    "general": ["company", "service", "panel", "support", "policy", "about" ,"is from"],
    "faq": ["faq", "questions", "help", "how", "guidelines"],
}

# Define required entities for each intent
required_entities_for_intent = {
    "wismo": ["ORDER_ID_OR_TRACKING_ID"],
    "cancel": ["ORDER_ID"],
    "reschedule": ["ORDER_ID"],
    "general": [],
    "faq": [],
}

# Define common words that should NOT be classified as IDs
excluded_words = set([
    "where", "track", "status", "cancel", "refund", "need", "tell", "what", "update",
    "modify", "order", "delivery", "shipment", "item", "product", "purchase", "check",
    "me", "my", "your", "the", "a", "an", "is", "of", "to", "for", "in", "it", "this",
    "number", "id", "date" # Added "date"
])

# --- Specific ID Patterns ---
id_patterns = {
    "ORDER_ID": [
        r'(?:order\s*id|order\s*#|purchase\s*id)\s*[:=\s]?\s*([A-Za-z0-9]{4,20})\b',
        r'\b(\d{5,15})\b', # Purely numeric order IDs
        r'\b([A-Z]{2,5}\d{4,15}[A-Z]{0,5})\b', # Alpha-numeric order IDs (e.g., AB12345C)
        r'\b([A-Z0-9]{6,15})\b', # More general alphanumeric, minimum 6 characters
    ],
    "TRACKING_ID": [
        # Explicit phrases
        r'(?:tracking\s*id|tracking\s*number|tracking\s*#|track\s*num)\s*[:=\s]?\s*([A-Za-z0-9-]{10,35})\b', # Increased max length
        # Common carrier-specific patterns (YOU MUST CUSTOMIZE THESE!)
        r'\b(1Z[A-Z0-9]{16})\b', # Example: UPS tracking number
        r'\b(94\d{20,25})\b', # Example: USPS tracking number (long numeric)
        r'\b([A-Z]{2}\d{9}[A-Z]{2})\b' # Example: Royal Mail/PostNL international format
    ],
    "CARRIER_ID": [
        r'(?:carrier\s*id|carrier\s*code|shipping\s*company)\s*[:=\s]?\s*([A-Za-z0-9]{2,10})\b',
        r'\b(FEDEX|UPS|DHL|USPS|AMAZONLOGISTICS|BLUEDART|DELHIVERY|EKART)\b'
    ]
}

def is_valid_date_format(date_string):
    """
    Attempts to parse a string into common date formats.
    Returns the parsed date in YYYY-MM-DD format if successful, otherwise None.
    Made stricter to avoid misinterpreting long numbers as dates.
    """
    if date_string.isdigit() and len(date_string) > 14: # Example: If purely numeric and longer than YYYYMMDDHHMMSS, likely not a date
        return None

    date_formats = [
        "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y",
        "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
        "%Y%m%d", # YYYYMMDD
        "%m%d%Y", # MMDDYYYY
        "%d%m%Y", # DDMMYYYY
        "%B %d, %Y", "%b %d, %Y",
        "%d %B %Y", "%d %b %Y",
        "%Y-%m-%dT%H:%M:%S", # ISO format for some timestamps
        "%Y%m%d%H%M%S" # YYYYMMDDHHMMSS - common numeric timestamp
    ]
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            # Add a reasonable year range check (e.g., within 5 years of current year)
            current_year = datetime.now().year
            if parsed_date.year >= (current_year - 5) and parsed_date.year <= (current_year + 5):
                return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def extract_info(text):
    doc = nlp(text)
    entities = {}
    lower_text = text.lower()

    # --- Step 1: Extract Explicit IDs First Based on Keywords ---
    # Prioritize IDs mentioned with clear context ("tracking ID is", "order ID is")
    
    # Try to extract Tracking ID (highest priority for explicit mention)
    for pattern in id_patterns.get("TRACKING_ID", []):
        match = re.search(pattern, lower_text)
        if match:
            extracted_id = match.group(1).upper().replace('-', '').strip()
            if len(extracted_id) > 5 and extracted_id.lower() not in excluded_words:
                entities["TRACKING_ID"] = extracted_id
                break # Break from patterns for TRACKING_ID if found, move to next ID type (ORDER_ID)

    # Try to extract Order ID (high priority for explicit mention)
    for pattern in id_patterns.get("ORDER_ID", []):
        match = re.search(pattern, lower_text)
        if match:
            extracted_id = match.group(1).upper().replace('-', '').strip()
            if len(extracted_id) >= 4 and extracted_id.lower() not in excluded_words:
                # Crucial: Only add if not already extracted as a TRACKING_ID (if your IDs can overlap)
                if "TRACKING_ID" in entities and entities["TRACKING_ID"] == extracted_id:
                    pass # Already identified as tracking ID, don't overwrite with Order ID
                else:
                    entities["ORDER_ID"] = extracted_id
                    break # Found an order ID, move to next ID type (CARRIER_ID)

    # Extract Carrier ID (can exist alongside order/tracking IDs)
    for pattern in id_patterns.get("CARRIER_ID", []):
        match = re.search(pattern, lower_text)
        if match:
            extracted_id = match.group(1).upper().strip() # Carrier IDs might not need hyphen removal
            if len(extracted_id) >= 2 and extracted_id.lower() not in excluded_words:
                entities["CARRIER_ID"] = extracted_id
                # No break here, as a message might contain a Carrier ID AND a Tracking ID


    # --- Step 2: Handle relative and explicit dates ---
    # First, handle explicit relative dates based on keywords
    days_ago_match = re.search(r'(\d+)\s*days? ago', lower_text)
    if days_ago_match:
        num_days = int(days_ago_match.group(1))
        actual_date = (datetime.now() - timedelta(days=num_days)).strftime("%Y-%m-%d")
        entities["order_date"] = actual_date
    elif "yesterday" in lower_text:
        entities["order_date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in lower_text:
        entities["order_date"] = datetime.now().strftime("%Y-%m-%d")
    elif "tomorrow" in lower_text:
        entities["order_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Then, look for purely numeric/formatted date strings that *haven't* been identified as IDs
    if "order_date" not in entities: # Only try parsing if no relative date was found
        # Find all sequences of numbers (and optional delimiters) that might be dates
        potential_date_strings = re.findall(r'\b(\d{4}[-/]?\d{2}[-/]?\d{2})\b|\b(\d{2}[-/]?\d{2}[-/]?\d{4})\b|\b(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b|\b(\d{8,14})\b', lower_text)
        for date_tuple in potential_date_strings:
            potential_date_str = ''.join(filter(None, date_tuple)).replace('/', '').replace('-', '').replace('.', '') # Clean up
            # Only process if this string hasn't been identified as an ID already
            if (potential_date_str not in entities.get("ORDER_ID", "") and
                potential_date_str not in entities.get("TRACKING_ID", "") and
                potential_date_str not in entities.get("CARRIER_ID", "")):
                
                parsed_date = is_valid_date_format(potential_date_str)
                if parsed_date:
                    entities["order_date"] = parsed_date
                    break # Found a valid date, stop searching for dates
            if "order_date" in entities: # Break outer loop if date found
                break

    # Fallback to spaCy's DATE entity if no specific date was found yet (and not already an ID)
    if "order_date" not in entities:
        for ent in doc.ents:
            if ent.label_ == "DATE":
                potential_date_str = ent.text.lower().replace('/', '').replace('-', '').replace('.', '')
                # Ensure spaCy's date entity isn't already an ID
                if (potential_date_str not in entities.get("ORDER_ID", "") and
                    potential_date_str not in entities.get("TRACKING_ID", "") and
                    potential_date_str not in entities.get("CARRIER_ID", "")):
                    
                    parsed_from_spacy = is_valid_date_format(ent.text)
                    if parsed_from_spacy:
                        entities["order_date"] = parsed_from_spacy
                    else:
                        entities["order_date"] = ent.text # Keep spaCy's text if not fully parseable
                    break


    # --- Step 3: Detect intent based on keywords ---
    detected_intent = "unknown"
    for intent, keywords in intent_keywords.items():
        if any(word in lower_text for word in keywords):
            detected_intent = intent
            break

    # --- Step 4: Validate required entities for intent ---
    missing_entities = []
    if detected_intent == "wismo" and "ORDER_ID_OR_TRACKING_ID" in required_entities_for_intent.get(detected_intent, []):
        if "ORDER_ID" not in entities and "TRACKING_ID" not in entities:
            missing_entities.append("ORDER_ID_OR_TRACKING_ID")
    elif detected_intent in required_entities_for_intent:
        for entity in required_entities_for_intent[detected_intent]:
            if entity not in entities:
                missing_entities.append(entity)

    return {"intent": detected_intent, "entities": entities, "missing": missing_entities}


# # Example test cases
# messages = [
#     "User Message: Cancel my order 45321.",                 # ORDER_ID: 45321
#     "User Message: Where is my package? My tracking ID is 9412345678901234567890", # Should be TRACKING_ID only
#     "User Message: Track my shipment 789XYZ.",
#     "User Message: I need to reschedule my order.",
#     "User Message: Tell me about your company.",
#     "User Message: What is the refund policy?",
#     "User Message: jdjskdjskdsk",
#     "User Message: my order ID is ABCDEFG123",
#     "User Message: I want to know the status of order #XYZ-9876",
#     "User Message: Can you check order 1234567890",
#     "User Message: Update my order 12345",
#     "User Message: Can you find the status of my order id = 12345",
#     "User Message: Where is my order with tracking number TRK123456789",
#     "User Message: I placed an order yesterday",
#     "User Message: Is my item 9876 in stock?",
#     "User Message: The invoice number is INV54321",
#     "User Message: What is the status of order ABCDEFGHIJKLMN",
#     "User Message: My carrier ID is FEDEX",
#     "User Message: How do I track using carrier code UPS?",
#     "User Message: My tracking number is 1Z9999W99999999999 and order is XYZ123",
#     "User Message: Where is my package? My tracking ID is 9412345678901234567890", # Long numeric tracking ID
#     "User Message: Can you help me with carrier id DHL?",
#     "User Message: Status of order 8745",
#     "User Message: My tracking is 9876543210",
#     "User Message: My order was placed on 2024-05-23", # Explicit YYYY-MM-DD date
#     "User Message: I placed it on 05/23/2024",       # Explicit MM/DD/YYYY date
#     "User Message: What is the status of order 20250523", # Ambiguous: should be date if not explicit ID
#     "User Message: My order ID is 20250523", # Explicitly stated as Order ID (Context overrides date)
#     "User Message: My delivery date is 23-05-2025", # DD-MM-YYYY date
#     "User Message: I ordered on May 23, 2025", # Textual date
#     "User Message: Order is from 20240101", # YYYYMMDD date
#     "User Message: This is a random string 123456789012345678901234567890", # Long number that's not an ID or date
#     "User Message: check order 2024-05-23", # Both order and date, prioritize order or context
#     "User Message: track 98765432109876543210", # Long numeric tracking ID (no explicit 'tracking ID')
# ]

# print("\n--- Extracted Intent & Differentiated IDs & Dates ---")
# for msg in messages:
#     print(f"\nUser: {msg}")
#     result = extract_info(msg)
#     print("Result:", result)