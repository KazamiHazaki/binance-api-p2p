import os
import time
import hashlib
import hmac
import requests
from dotenv import load_dotenv
import google.auth
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Load environment variables from the .env file
load_dotenv()

# Get API credentials from environment variables
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
ads_no = os.getenv("ADS_NO")
json_key_path = os.getenv("JSON_KEY_PATH")
spreadsheet_id = os.getenv("SPREADSHEET_ID")
range_name = os.getenv("RANGE_NAME")

# Check if the variables are loaded correctly
if not api_key or not api_secret or not ads_no or not json_key_path or not spreadsheet_id or not range_name:
    print("API credentials or required variables are missing in the .env file.")
    exit(1)

# API request to get price data
timestamp = int(time.time() * 1000)
query_string = f"adsNo={ads_no}&timestamp={timestamp}"
signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

url = f"https://api.binance.com/sapi/v1/c2c/ads/getDetailByNo?{query_string}&signature={signature}"
headers = {
    'X-MBX-APIKEY': api_key
}

# Make the request
response = requests.post(url, headers=headers)
data = response.json()

# Check if the response is successful
if data.get('code') == '000000' and data.get('success'):
    price = data['data']['price']
    print(f"Price: {price}")

    # Authenticate using the service account
    credentials = Credentials.from_service_account_file(
        json_key_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    # Build the Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Prepare the data to send
    values = [
        [price]
    ]
    
    body = {
        'values': values
    }

    # Call the Sheets API to append data to the sheet
    sheet = service.spreadsheets()
    result = sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"Data appended to sheet: {result}")
else:
    print(f"Failed to retrieve price data: {data.get('message', 'No message provided')}")
