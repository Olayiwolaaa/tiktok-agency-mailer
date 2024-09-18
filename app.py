import requests
import re
import csv
import env

BASE_URL = env.X_BASE_URL
HEADERS = {
    "x-project-name": env.X_PROJECT_NAME,
    "x-api-key": env.X_API_KEY
}

# List of keywords to iterate through
keywords_list = env.KEYWORDS

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
def get_rawdata_for_keyword(keyword, csv_writer):
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
                
                # Write email and username to CSV file
                csv_writer.writerow([email, f"https://tiktok.com/@{display_id}"])
        
        # Check if there's no more data
        if has_more == 0:
            print(f"No more data for keyword: {keyword}.")
            break

        # Increase offset for next iteration
        offset += 10
        
        # Increment request count and pause every 5 requests
        request_count += 1

# Iterate through each keyword in the keywords list and write to CSV file
def get_rawdata():
    with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Emails', 'Usernames'])  # Write header row
        for keyword in keywords_list:
            get_rawdata_for_keyword(keyword, csv_writer)
            print("Moving to the next keyword...\n")

# Run the function
get_rawdata()
