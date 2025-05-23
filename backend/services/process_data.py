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
    "wismo": ["ORDER_ID_OR_TRACKING_NUMBER"],
    "cancel": ["ORDER_ID", "TRACKING_NUMBER"],
    "reschedule": ["ORDER_ID","TRACKING_NUMBER"],
    "general": [],
    "faq": [],
}

# Define common words that should NOT be classified as IDs
excluded_words = set([
    "where", "track", "status", "cancel", "refund", "need", "tell", "what", "update",
    "modify", "order", "delivery", "shipment", "item", "product", "purchase", "check",
    "me", "my", "your", "the", "a", "an", "is", "of", "to", "for", "in", "it", "this",
    "number", "id", "date", # Original words
    "from", "on", "by", "with", # ADDED "with" and other common prepositions/conjunctions
    "and", "or", "but", "so", "then", "also", "just", "please", "can", "could", "would",
    "traking", "trackingnumber",
    "awb",
])

# --- Specific ID Patterns ---
id_patterns = {
    "ORDER_ID": [
      # New Pattern: Catches any alphanumeric string directly following "order", "order is", "order ID is".
      # MODIFIED: Added '_' to the character set [A-Za-z0-9_-]
      r'(?:order|order\s*is|order\s*id\s*is)\s*([A-Za-z0-9_-]{4,30})\b',

      # Pattern 1: Explicitly stated order ID (e.g., "order id: ABC123", "purchase #XYZ")
      # CONSIDER: If your explicit IDs can have underscores, add '_' here too: [A-Za-z0-9_]{4,20}
      r'(?:order\s*id|order\s*#|purchase\s*id)\s*[:=\s]?\s*([A-Za-z0-9]{4,20})\b', # Keep as is or modify based on your ID format

      # Pattern 2: Purely numeric order ID (e.g., "my order 12345")
      # No change needed, as underscores are not numeric.
      r'\b(\d{5,15})\b',

      # Pattern 3: Structured alphanumeric order ID (e.g., "AB12345C", "INV98765")
      # No change needed, as underscores are not typically in this type of structured ID.
      r'\b([A-Z]{2,5}\d{4,15}[A-Z]{0,5})\b',

      # Pattern 4: General alphanumeric order ID (e.g., "XYZABC01", "EFNFNKN")
      # CONSIDER: If your general alphanumeric IDs can have underscores, add '_' here: [A-Z0-9_]{6,15}
      r'\b([A-Z0-9]{6,15})\b', # Keep as is or modify based on your ID format
    ],
    "TRACKING_NUMBER": [
        # HIGH PRIORITY PATTERN: Catches alphanumeric strings (with hyphens/underscores) following
        # various tracking and AWB keywords/phrases.
        # This pattern is made more robust by explicitly defining the full keyword phrases in non-capturing groups.
        # Includes variations like "trackingnumber" (one word) and common typos like "traking".
        # Also handles "awb number" as a full phrase, and "awb" or "track" as standalone keywords.
        # Reduced min length to 3 to catch shorter IDs when explicitly preceded by a keyword.
        r'(?:track(?:ing)?\s*(?:number)?|traking|awb(?:\s*number|\s*is)?)\s*([A-Za-z0-9_-]{3,35})\b',

        # SECONDARY PATTERN: Explicit phrases for tracking IDs that use "id" or "#" as separators.
        # This handles cases like "tracking ID: 123ABC" or "tracking #XYZ-987".
        r'(?:tracking\s*id|tracking\s*#|track\s*num)\s*[:=\s]?\s*([A-Za-z0-9_-]{10,35})\b', 
        
        # Carrier-specific tracking patterns. These are often very specific formats.
        r'\b(1Z[A-Z0-9]{16})\b',    # Example: UPS tracking number
        r'\b(94\d{20,25})\b',      # Example: USPS tracking number (long numeric)
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
    
    for pattern in id_patterns.get("TRACKING_NUMBER", []):
        match = re.search(pattern, lower_text)
        if match:
            # Ensure proper cleaning for underscores and hyphens.
            extracted_id = match.group(1).replace('-', '').replace('_', '').strip()
            # The min length check is now mostly handled by the regex itself (e.g., {3,35}).
            # We just need to check against the excluded words.
            if extracted_id.lower() not in excluded_words:
                entities["TRACKING_NUMBER"] = extracted_id
                break # Break from patterns for TRACKING_NUMBER if found

    # Try to extract Order ID (high priority for explicit mention)
    for pattern in id_patterns.get("ORDER_ID", []):
        match = re.search(pattern, lower_text)
        if match:
            extracted_id = match.group(1).replace('-', '').strip()
            if len(extracted_id) >= 4 and extracted_id.lower() not in excluded_words:
                # Crucial: Only add if not already extracted as a TRACKING_NUMBER (if your IDs can overlap)
                if "TRACKING_NUMBER" in entities and entities["TRACKING_NUMBER"] == extracted_id:
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
                potential_date_str not in entities.get("TRACKING_NUMBER", "") and
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
                    potential_date_str not in entities.get("TRACKING_NUMBER", "") and
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
    if detected_intent == "wismo" and "ORDER_ID_OR_TRACKING_NUMBER" in required_entities_for_intent.get(detected_intent, []):
        if "ORDER_ID" not in entities and "TRACKING_NUMBER" not in entities:
            missing_entities.append("ORDER_ID_OR_TRACKING_NUMBER")
    elif detected_intent in required_entities_for_intent:
        for entity in required_entities_for_intent[detected_intent]:
            if entity not in entities:
                missing_entities.append(entity)

    return {"intent": detected_intent, "entities": entities, "missing": missing_entities}


# Example test cases
# messages = [
#     "User Message: Cancel my track FEWHKWFIU.",             
#     "User Message: Cancel my trackingnumber efnfnkn.",  
#         "User Message: Cancel my traking ejfjkfnfnkn.", 
#         "User Message: Cancel my awb kdf.",  
 

#     "User Message: Cancel my aws n efn63427_fnkn.",                 # ORDER_ID: 45321

#                    # ORDER_ID: 45321
# # ORDER_ID: 45321
# ]

# print("\n--- Extracted Intent & Differentiated IDs & Dates ---")
# for msg in messages:
#     print(f"\nUser: {msg}")
#     result = extract_info(msg)
#     print("Result:", result)