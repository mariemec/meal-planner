import requests
import json

def get_grocery_deals(zip_code):
    # 1. Define the search parameters
    # Flipp uses a specific 'backflipp' endpoint for searches
    url = "https://backflipp.wishabi.com/flipp/items/search"

    params = {
        "postal_code": zip_code,
        "q": "groceries",  # Broad search for all grocery items
        "locale": "en-us"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        deals = []
        for item in data.get('items', []):
            # We filter for items that actually have a price listed
            if item.get('current_price'):
                deal = {
                    "store": item.get('merchant_name'),
                    "item": item.get('name'),
                    "price": float(item.get('current_price')),
                    "unit": item.get('unit_standard_name'), # e.g., 'lb' or 'oz'
                    "valid_until": item.get('valid_to')
                }
                deals.append(deal)

        return deals

    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []

# Execute for your area
zip_94306_deals = get_grocery_deals("94306")

# Print the first 5 deals to verify
for d in zip_94306_deals[:5]:
    print(f"[{d['store']}] {d['item']} - ${d['price']}")