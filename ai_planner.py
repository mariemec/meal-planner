import os
import pandas as pd
from google import genai
from google.genai import types

def generate_plan():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    csv_file = 'flyer_items_94306.csv'
    if not os.path.exists(csv_file):
        print("CSV not found!")
        return

    df = pd.read_csv(csv_file)
    sample_deals = df.head(100).to_string(index=False)

    pantry_spices = [
        "Salt", "Black Pepper", "Garlic Powder", "Onion Powder", "Cumin", 
        "Paprika", "Smoked Paprika", "Chili Powder", "Red Pepper Flakes", 
        "Cayenne Pepper", "Thyme", "Sage", "Bay Leaves", "Italian Seasoning", 
        "Cinnamon", "Nutmeg", "Ground Ginger", "Coriander", "Cardamom", 
        "Cloves", "Allspice", "Garam Masala"
    ]

    prompt = f"""
    You are an elite Culinary Consultant and Meal Planner. 
    The goal is to provide a 7-day dinner plan for two that is sophisticated, diverse, and chef-quality, while strictly adhering to a $100 weekly grocery budget in Palo Alto (94306).

    USER PANTRY (Use these freely, do not buy):
    Spices: {', '.join(pantry_spices)}
    Staples: Oil, Flour, Sugar, Water.

    CONSTRAINTS:
    1. EXCLUDE recipes requiring: Basil, Oregano, Rosemary, Dill, Tarragon, Turmeric, Mustard Powder, Celery Seed, Fennel, Star Anise, Sumac, Sesame, or Poppy seeds (unless they are on sale in the data).
    2. SOURCES: Prioritize recipes from reputable chefs (e.g., J. Kenji López-Alt, Samin Nosrat) or magazines (e.g., Bon Appétit, NYT Cooking, Saveur, Food & Wine, Milk Street). 
    3. NO 'CHEAP' SHORTCUTS: Focus on technique-driven recipes that use the sale items as the star.
    4. SHOPPING: Be mindful that Palo Alto prices are high. The $100 must cover all non-pantry items.

    FORMAT:
    - Day [X]: [Dish Name]
    - Source/Chef: [e.g., Bon Appétit / Molly Baz]
    - Recipe Link: [Verified URL]
    - Key Sale Ingredients: [List items used from CSV]
    - Spice Profile: [Which pantry spices make this dish shine?]
    - Budget Note: [Why this fits the $100 limit]

    GROCERY DATA:
    {sample_deals}
    """

    # We use 'google_search' tool to help the AI find valid, non-broken links
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    
    print(response.text)
    
    with open("meal_plan.txt", "w") as f:
        f.write(response.text)

if __name__ == "__main__":
    generate_plan()