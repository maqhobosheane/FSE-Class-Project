import requests
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Matplotlib configuration to run in  Docker
plt.switch_backend('Agg')

API_URL = "https://api.coingecko.com/api/v3/coins/ripple/market_chart"

def generate_price_chart_image():
    """
    Fetches price data and generates a PNG chart image with a dark theme in memory.
    Returns a file-like object (BytesIO) or None on error.
    """
    try:
        params = { 'vs_currency': 'usd', 'days': '7', 'interval': 'daily' }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = data.get('prices', [])

        if not prices:
            return None

        # Extract dates and prices for plotting
        dates = [datetime.fromtimestamp(p[0] / 1000) for p in prices]
        price_values = [p[1] for p in prices]

        # --- Matplotlib Chart Generation ---
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6))

        
        # Set the outer background color of the figure
        fig.patch.set_facecolor('#1C1C1C') 
        # Set the inner background color of the plotting area
        ax.set_facecolor('#2A2A2A')

        ax.plot(dates, price_values, marker='o', linestyle='-', color='#00AEEF', label='XRP Price')

        # Formatting the chart
        ax.set_title('XRP Price History (Last 7 Days)', color='white', fontsize=16, pad=20)
        ax.set_ylabel('Price (USD)', color='white', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.2)
        fig.autofmt_xdate() # Auto-rotate date labels

        # Set text and border colors
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#555555') # A slightly softer gray for borders

        
        buf = io.BytesIO()
        # Set transparent=False to include the background colors
        plt.savefig(buf, format='png', transparent=False, bbox_inches='tight', dpi=100)
        buf.seek(0) # Rewind the buffer to the beginning
        plt.close(fig) # Close the figure to free up memory

        return buf

    except requests.exceptions.RequestException as e:
        print(f"--- API request FAILED: {e} ---")
        return None
    except Exception as e:
        print(f"--- Chart generation FAILED: {e} ---")
        return None
