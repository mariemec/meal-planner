import os
import smtplib
import pandas as pd
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types

# --- SPOONACULAR INTEGRATION ---

def get_verified_recipe(query):
    """Fetches exact ingredients and source URL from Spoonacular."""
    api_key = os.environ.get("SPOONACULAR_API_KEY")
    url = "https://api.spoonacular.com/recipes/complexSearch"
    
    params = {
        "apiKey": api_key,
        "query": query,
        "number": 1,
        "fillIngredients": True,
        "addRecipeInformation": True
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data['results']:
            recipe = data['results'][0]
            return {
                "title": recipe['title'],
                "url": recipe['sourceUrl'],
                "ingredients": [i['original'] for i in recipe['extendedIngredients']],
                "aisles": [i['aisle'] for i in recipe['extendedIngredients']]
            }
    except Exception as e:
        print(f"Spoonacular error for {query}: {e}")
    return None

# --- MAIN APP LOGIC ---

def generate_meal_plan():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    # 1. Load your flyer deals
    df = pd.read_csv('flyer_items.csv').head(100)
    deals_summary = df.to_string(index=False)

    # 2. ASK GEMINI FOR IDEAS BASED ON DEALS
    idea_prompt = f"""
    Based on these grocery deals, suggest 7 dinner meal titles for two people.
    DEALS:
    {deals_summary}
    Return ONLY a bulleted list of 7 meal names, nothing else.
    """
    
    idea_response = client.models.generate_content(model="gemini-2.0-flash", contents=idea_prompt)
    meal_ideas = [line.strip("- ").strip() for line in idea_response.text.strip().split("\n") if line]

    # 3. FETCH DATA FROM SPOONACULAR FOR EACH IDEA
    verified_recipes_data = []
    print("Verifying recipes with Spoonacular...")
    for idea in meal_ideas[:7]: # Ensure we only do 7
        data = get_verified_recipe(idea)
        if data:
            verified_recipes_data.append(data)

    # 4. FINAL PASS: GEMINI CALCULATES BUDGET & FORMATS
    final_prompt = f"""
    You are a Michelin-star Culinary Consultant. 
    Use the VERIFIED ingredient lists below to create a 7-day plan.
    
    BUDGET: $100 total. 
    FLYER PRICES: 
    {deals_summary}
    
    VERIFIED RECIPE DATA (USE THESE EXACT INGREDIENTS):
    {verified_recipes_data}

    PANTRY (FREE): Salt, Pepper, Oil, Flour, Sugar, Garlic Powder, Onion Powder.

    OUTPUT FORMAT:
    ## SECTION 1: THE CULINARY PLAN
    ---
    ### Day [X]: [Dish Name]
    * **Source:** [URL to the recipe]
    * **Full Ingredient Check:** List every ingredient from the verified list and note if it's a 'Sale Item' or 'Estimated Cost'.
    * **Financial Sanity Check:** Itemized cost total for this meal.

    ## SECTION 2: CONSOLIDATED SHOPPING LIST
    (Group by Store/Aisle)
    """

    final_response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=final_prompt
    )
    
    return final_response.text

def send_email_notification(content):
    # (Existing email logic remains the same)
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    msg = MIMEMultipart()
    msg['Subject'] = "🍽 Verified Michelin-Star Meal Plan"
    msg['From'] = f"Grocery Bot <{sender}>"
    msg['To'] = receiver
    msg.attach(MIMEText(content, 'plain'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    print("Generating plan...")
    meal_plan = generate_meal_plan()
    print("Sending email...")
    send_email_notification(meal_plan)
    print("Success!")