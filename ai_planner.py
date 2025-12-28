import os
import pandas as pd
from google import genai
from google.genai import types

def generate_plan():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    csv_file = f'flyer_items.csv'
    if not os.path.exists(csv_file):
        print(f"CSV {csv_file} not found!")
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
    You are an elite Michelin-star Culinary Consultant. 
    Task: Provide a 7-day dinner plan for two ($100 max).
    
    PANTRY (Use these freely): {', '.join(pantry_spices)}, Oil, Flour, Sugar.
    
    STRICT CONSTRAINTS:
    1. VERIFIED URLS: You MUST provide a direct, clickable URL for every recipe. Do not say "See notes" or "I will adapt." The link must be a real, functional recipe from a top-tier source (NYT Cooking, Bon Appétit, Serious Eats, etc.).
    2. BUDGET MATHEMATICS: You must perform a "Sanity Check" calculation for every meal. If a meal uses 1lb of $14.99 steak, you only have $85 left for the other 6 days. Do not exceed $100 total.
    3. STORE OPTIMIZATION: Consolidate shopping to a maximum of 2 stores unless a 3rd store saves >$15.
    4. NO HALLUCINATIONS: If the grocery data does not contain a specific vegetable or side dish, you must list its estimated cost in the shopping list (e.g., "Onion (est. $0.80)").

    REQUIRED OUTPUT FORMAT:

    ## SECTION 1: THE CULINARY PLAN
    ---
    ### Day [X]: [Dish Name]
    * **Chef/Source:** [Name]
    * **Recipe Link:** [Direct URL]
    * **Sale Items:** [Items from CSV]
    * **Non-Sale Items:** [Items NOT in CSV with estimated prices]
    * **Pantry Items:** [Items from pantry list, no cost]
    * **Financial Sanity Check:** [Item Cost] + [Estimated Cost of non-sale items] = [Meal Total].
    
    ## SECTION 2: CONSOLIDATED SHOPPING LIST
    (Grouped by STORE and AISLE. Include estimated prices for items NOT in the CSV so the user knows the true total.)

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