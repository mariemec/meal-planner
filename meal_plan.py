import requests
import time

def get_grocery_deals(zip_code):
    url = "https://backflipp.wishabi.com/flipp/items/search"
    categories = ["meat", "produce", "dairy", "bakery", "pantry"]
    all_deals = []
    
    headers = {"User-Agent": "Mozilla/5.0"}

    for cat in categories:
        offset = 0
        limit = 100  # Request 100 items at a time
        
        while True:
            params = {
                "postal_code": zip_code,
                "q": cat,
                "locale": "en-us",
                "offset": offset,
                "limit": limit
            }
            
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break # No more items in this category, stop the loop
            
            for item in items:
                if item.get('current_price'):
                    all_deals.append({
                        "store": item.get('merchant_name'),
                        "item": item.get('name'),
                        "price": float(item.get('current_price')),
                        "category": cat
                    })
            
            # Move to the next "page"
            offset += limit
            
            # Optional: Short sleep to be polite to Flipp's servers
            time.sleep(0.5)
            
            # Safety break: don't get more than 500 items per category
            if offset > 500:
                break

    # Clean up: remove exact duplicates
    unique_deals = {f"{d['store']}{d['item']}": d for d in all_deals}.values()
    return list(unique_deals)