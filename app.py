import requests
import re
import time
import env

BASE_URL = "https://api.tokapi.online/v1/search/live"
HEADERS = {
    "x-project-name": X_PROJECT_NAME,
    "x-api-key": X_API_KEY
}

# List of keywords to iterate through
keywords_list = [
    "Livestreaming",
    "Gameplay",
    "Followers",
    "Chat interaction",
    "Subscriber",
    "Stream schedule",
    "Affiliate",
    "Partner",
    "Stream overlay",
    "Bits",
    "Emotes",
    "Raid",
    "Hosting",
    "Viewers",
    "Clips",
    "Donation",
    "Streamlabs",
    "Stream highlights",
    "Twitch chat bots",
    "VOD (Video on Demand)"
]

PARAMS = {
    "region": "GB",
    "count": 10,
}

# Regex to find email pattern
email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

# Function to extract follower count from rawdata using regex
def extract_follower_count(rawdata):
    match = re.search(r'"follower_count":(\d+)', rawdata)
    return int(match.group(1)) if match else 0

# Function to extract bio_description from rawdata using regex
def extract_bio_description(rawdata):
    match = re.search(r'"bio_description":"(.*?)"', rawdata)
    return match.group(1) if match else ""

# Function to extract email from bio_description using regex
def extract_email(bio_description):
    match = re.search(email_pattern, bio_description)
    return match.group(0) if match else None

# Function to extract display_id (username) using regex
def extract_display_id(rawdata):
    match = re.search(r'"display_id":"(.*?)"', rawdata)
    return match.group(1) if match else None

# Function to fetch and process raw data for a specific keyword
def get_rawdata_for_keyword(keyword):
    offset = 1
    request_count = 0  # Counter to keep track of requests
    
    print(f"Processing keyword: {keyword}")

    while True:
        PARAMS['offset'] = offset
        PARAMS['keyword'] = keyword  # Set the current keyword
        
        response = requests.get(BASE_URL, headers=HEADERS, params=PARAMS)
        
        data = response.json()
        
        # Check if there's more data
        has_more = data.get('has_more', 0)
        if not data or 'data' not in data:
            break

        # Loop through each item in data
        for item in data['data']:
            # Extract rawdata
            raw_data_str = item.get('lives', {}).get('rawdata', '')
            
            if raw_data_str:
                # Extract follower_count and bio_description
                follower_count = extract_follower_count(raw_data_str)
                bio_description = extract_bio_description(raw_data_str)
                
                # Extract email from bio_description
                email = extract_email(bio_description)

                # Extract username (display_id)
                display_id = extract_display_id(raw_data_str)

                # Skip if no email or follower count > 100k
                if not email or follower_count > 100000:
                    continue
                
                # Print email, username, and follower count
                print(f"Email: {email}, Username: https://tiktok.com/@{display_id}, Follower Count: {follower_count}")
        
        # Check if there's no more data
        if has_more == 0:
            print(f"No more data for keyword: {keyword}.")
            break

        # Increase offset for next iteration
        offset += 10
        
        # Increment request count and pause every 5 requests
        request_count += 1

# Iterate through each keyword in the keywords list
def get_rawdata():
    for keyword in keywords_list:
        get_rawdata_for_keyword(keyword)
        print("Moving to the next keyword...\n")

# Run the function
get_rawdata()
