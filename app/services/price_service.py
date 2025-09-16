import requests
from datetime import datetime, timedelta

API_URL = "https://api.coingecko.com/api/v3/coins/ripple/market_chart"

def get_price_history():
    """
    Fetches the last 7 days of XRP price data from the CoinGecko API.
    """
    print("--- Attempting to call CoinGecko API... ---") # <-- DEBUG
    try:
        params = {
            'vs_currency': 'usd',
            'days': '7',
            'interval': 'daily'
        }
        
        # Add a timeout to your request
        response = requests.get(API_URL, params=params, timeout=10) # <-- ADD TIMEOUT
        response.raise_for_status()

        print("--- API call successful! Formatting data... ---") # <-- ADD THIS

        data = response.json()
        prices = data.get('prices', [])

        if not prices:
            return "Could not retrieve price data at this time."

        formatted_message = "*XRP Price History (Last 7 Days):*\n\n"
        for price_entry in prices:
            timestamp_ms, price = price_entry
            date_obj = datetime.fromtimestamp(timestamp_ms / 1000)
            date_str = date_obj.strftime('%Y-%m-%d')
            formatted_message += f"- {date_str}: `${price:,.4f}`\n"
            
        return formatted_message

    except requests.exceptions.RequestException as e:
        print(f"--- API request FAILED: {e} ---") # <-- ADD THIS FOR ERRORS
        return "Sorry, there was an error fetching the price data. Please try again later."