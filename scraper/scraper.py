"""
Real-time Airfare Price Index (APIx) - Playwright Scraper
Author: APIx Hackathon Team
Target: Google Flights (aggregates IndiGo, Air India, Akasa, SpiceJet)
Output: data/raw_fares.csv
"""

import os
import re
import csv
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================
ROUTES = ["DEL-BOM", "DEL-BLR"]  # Target routes
ADVANCE_DAYS_LIST = [1, 15]      # Tomorrow (1 day) and 15 days out
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "raw_fares.csv")

CSV_HEADERS = [
    "route",
    "airline",
    "scrape_date",
    "travel_date",
    "advance_days",
    "base_fare",
    "tax",
    "total_fare",
]

# List of major domestic carriers in India to match against
KNOWN_AIRLINES = [
    "IndiGo",
    "Air India",
    "Air India Express",
    "Akasa Air",
    "SpiceJet",
    "Vistara",
    "Alliance Air",
]


def clean_price(price_str: str) -> str:
    """
    Strips currency symbols (₹, INR), commas, and spaces.
    Example: '₹5,432' -> '5432'
    """
    digits_only = re.sub(r"[^\d]", "", price_str)
    return digits_only


def extract_airline_name(text: str) -> str:
    """
    Finds which known Indian airline appears in the flight card text.
    Defaults to 'Other / Multiple' if not directly matched.
    """
    for airline in KNOWN_AIRLINES:
        if airline.lower() in text.lower():
            return airline
    return "Other Airline"


def init_csv():
    """Ensures data directory and CSV file with headers exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        print(f"[INIT] Created {OUTPUT_FILE} with required schema.")


def append_records_to_csv(records):
    """Appends a list of flight rows to data/raw_fares.csv."""
    if not records:
        return
    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(records)
    print(f"[SAVED] Appended {len(records)} records to {OUTPUT_FILE}")


# ==========================================
# 2. MAIN SCRAPER LOGIC
# ==========================================
def scrape_flights():
    init_csv()

    today = date.today()
    scrape_date_str = today.strftime("%Y-%m-%d")

    print(f"Starting APIx Scraper | Scrape Date: {scrape_date_str}")
    print("=" * 60)

    # Launch Playwright in Chromium
    with sync_playwright() as p:
        # headless=False lets you watch the browser in action (great for debugging & demos)
        browser = p.chromium.launch(headless=False, slow_mo=50)
        
        # Set a standard desktop viewport and User-Agent to avoid bot triggers
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        page = context.new_page()

        for route in ROUTES:
            origin, destination = route.split("-")

            for advance_days in ADVANCE_DAYS_LIST:
                travel_date = today + timedelta(days=advance_days)
                travel_date_str = travel_date.strftime("%Y-%m-%d")

                print(f"\n--> Fetching: {route} | Travel Date: {travel_date_str} (+{advance_days}d)")

                # Direct Google Flights search URL with origin, destination, and date
                url = (
                    f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20"
                    f"from%20{origin}%20on%20{travel_date_str}%20oneway&curr=INR"
                )

                try:
                    # Step 1: Open results page
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)

                    # Step 2: Handle any Google cookie/consent pop-ups if they appear
                    try:
                        consent_btn = page.locator("button:has-text('Accept all'), button:has-text('I agree')")
                        if consent_btn.is_visible(timeout=3000):
                            consent_btn.first.click()
                    except Exception:
                        pass

                    # Step 3: Wait for JS-rendered flight cards to load
                    # Google Flights groups results inside list items with flight details
                    page.wait_for_selector("li[class*='pIav2d'], div[role='listitem']", timeout=20000)
                    time.sleep(2)  # Short safety pause for dynamic fare rendering

                    # Step 4: Extract flight listing cards
                    # We look for cards within "Best departing flights" or "Other departing flights"
                    flight_cards = page.locator("li[class*='pIav2d'], div[role='listitem']").all()

                    if not flight_cards:
                        print(f"    [WARN] No flight cards found for {route} on {travel_date_str}.")
                        continue

                    scraped_rows = []

                    for card in flight_cards:
                        card_text = card.inner_text()

                        # Check if card contains a price in ₹ / INR format
                        # Example matches: ₹5,432 or INR 5432
                        price_match = re.search(r"[₹]\s*([\d,]+)", card_text)
                        if not price_match:
                            continue  # Skip header or non-flight item cards

                        raw_price = price_match.group(1)
                        total_fare = clean_price(raw_price)
                        airline = extract_airline_name(card_text)

                        # In Indian search listing pages, DGCA mandates all-inclusive total fares.
                        # Base fare and tax are not broken down until checkout, so leave blank.
                        base_fare = ""
                        tax = ""

                        scraped_rows.append([
                            route,
                            airline,
                            scrape_date_str,
                            travel_date_str,
                            advance_days,
                            base_fare,
                            tax,
                            total_fare,
                        ])

                    print(f"    [OK] Successfully extracted {len(scraped_rows)} flights.")
                    append_records_to_csv(scraped_rows)

                except Exception as e:
                    # Basic error handling to ensure one failing route does not kill the entire run
                    print(f"    [ERROR] Failed to scrape {route} on {travel_date_str}: {str(e)[:120]}...")
                    continue

        browser.close()
        print("\n" + "=" * 60)
        print(f"[DONE] All routes processed. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_flights()