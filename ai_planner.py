import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types
import markdown

def generate_meal_plan():
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

    REQUIRED OUTPUT FORMAT (Use Markdown):

    # 🍽 WEEKLY CULINARY PLAN
    
    ## 📊 BUDGET OVERVIEW
    * **Total Estimated Spend:** $[Total]
    * **Stores:** [Store names]
    
    | Day | Dish | Recipe Link | Est. Cost |
    | :--- | :--- | :--- | :--- |
    | 1 | [Name] | [Link] | $[Cost] |
    | ... | ... | ... | ... |

    ---

    ## 👨‍🍳 DAILY DETAILS
    
    ### 🗓 Day [X]: [Dish Name]
    * **Recipe:** [Direct URL]
    * **Grocery Items:** [Items + Prices]
    * **Pantry Items:** [Spices used]
    * **Cost Breakdown:** [Calculation]
    
    ---

    ## 🛒 CONSOLIDATED SHOPPING LIST
    
    ### [STORE NAME]
    * **[Aisle Name]**
        - [ ] Item 1 ($Price)
        - [ ] Item 2 ($Price)

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

    return response.text


def send_email_notification(content):
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    msg = MIMEMultipart()
    msg['Subject'] = "🍽 Your Weekly Grocery & Meal Plan"
    msg['From'] = f"Chef Gemini <{sender}>"
    msg['To'] = receiver

    # Convert Markdown to HTML for a professional email look
    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
          table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
          th {{ background-color: #f2f2f2; }}
          h1 {{ color: #2e7d32; }}
          h2 {{ border-bottom: 2px solid #2e7d32; padding-bottom: 5px; }}
        </style>
      </head>
      <body>
        {markdown.markdown(content, extensions=['tables'])}
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)


if __name__ == "__main__":
    # 1. Load Data
    data = pd.read_csv('flyer_items.csv').head(200).to_string()
    
    # 2. Run AI
    print("Generating plan...")
    meal_plan = generate_meal_plan()
    
    # 3. Deliver Results
    print("Sending email...")
    send_email_notification(meal_plan)
    
    print("All done!")