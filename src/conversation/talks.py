# ======================= libraries  ======================= #
import os
import json
import re

# ======================= variables  ======================= #
JSONPATH =  "src/conversation/small_talks.json"

def load_small_talks():
    """
    
    """
    if not os.path.exists(JSONPATH):
        raise FileNotFoundError(f"File not found: {os.path.abspath(JSONPATH)}")
    
    with open(JSONPATH, 'r', encoding='utf-8') as file:
        return json.load(file)
    

def clean_input(user_input):
    """
    
    """
    return re.sub(r'[^\w\s]', '', user_input).strip().lower()
    