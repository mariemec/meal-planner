import requests

def get_grocery_deals(zip_code):
    url = "https://backflipp.wishabi.com/flipp/items/search"
    # These keywords force Flipp to look past the "Featured" page
    categories = ["meat", "produce", "dairy", "bakery", "pantry"]
    all_deals = []
    
    headers = {"User-Agent": "Mozilla/5.0"}

    for cat in categories:
        params = {
            "postal_code": zip_code,
            "q": cat,
            "locale": "en-us"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            for item in data.get('items', []):
                # Clean up the data
                name = item.get('name')
                price = item.get('current_price')
                merchant = item.get('merchant_name')
                
                if price and name:
                    all_deals.append({
                        "store": merchant,
                        "item": name,
                        "price": float(price),
                        "category": cat
                    })
        except Exception as e:
            print(f"Error fetching {cat}: {e}")

    # Remove duplicates (sometimes an item is in two categories)
    unique_deals = {f"{d['store']}{d['item']}": d for d in all_deals}.values()
    return list(unique_deals)

# Test run
deals = get_grocery_deals("94306")
for d in deals[:10]: # Print top 10 to check variety
    print(f"[{d['category'].upper()}] {d['store']}: {d['item']} - ${d['price']}")