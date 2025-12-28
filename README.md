# 🛒 Gourmet Grocery Bot

An automated meal planning pipeline that scrapes local grocery flyers, analyzes deals using AI, and generates a chef-quality 7-day dinner plan and shopping list—all while maintaining a **$100/week budget**.

## 🚀 How It Works

1.  **`meal_plan.py`**: Scrapes the Flipp API for a specific zip code. It identifies grocery flyers (Sprouts, Lucky, Safeway, etc.), extracts every line item, and saves them into a structured `flyer_items_{zipcode}.csv`.
2.  **`ai_planner.py`**: 
    * Reads the CSV data.
    * Cross-references deals with your specific **pantry inventory**.
    * Uses **Gemini 2.0 Flash** with Google Search grounding to find high-end recipes (NYT Cooking, Bon Appétit, Serious Eats).
    * Optimizes the plan to minimize the number of stores visited to reduce travel time.
3.  **GitHub Actions**: A scheduler (`schedule.yml`) runs the entire sequence every Friday at 8:00 AM PST.

## 🛠 Setup

### 1. Prerequisites
* **Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/).

### 2. GitHub Secrets
To run this via GitHub Actions, add the following secret in **Settings > Secrets and variables > Actions**:
* `GEMINI_API_KEY`: Your Google AI API key.
* `ZIP_CODE` : Your zip code.

### 3. Repository Structure
```text
.github/workflows/
  └── schedule.yml          # The automation triggers
ai_planner.py               # AI logic and recipe matching
meal_plan.py                # Flipp API scraper
flyer_items_{zipcode}.csv   # Generated grocery data (auto-generated)
shopping_list.md            # Final output (auto-generated)