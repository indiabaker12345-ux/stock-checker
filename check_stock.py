"""
Stock checker for Meaco air conditioner across John Lewis, AO, and Currys.

How it works:
- Loads each product page in a real (headless) browser via Playwright,
  so JavaScript-rendered stock status is captured correctly.
- Looks for text signalling "in stock" vs "out of stock".
- Keeps track of the last known status for each site in stock_state.json,
  so it only emails you when something CHANGES from out-of-stock to in-stock
  (not every single run).
- Sends an email via Gmail SMTP if a product just came back in stock.
"""

import json
import os
import smtplib
import sys
from email.mime.text import MIMEText
from pathlib import Path

from playwright.sync_api import sync_playwright

STATE_FILE = Path(__file__).parent / "stock_state.json"

# Phrases that indicate the item is OUT of stock.
# If none of these are found, and the page loaded successfully,
# we assume it's in stock.
OUT_OF_STOCK_PHRASES = [
    "out of stock",
    "sold out",
    "currently unavailable",
    "not available",
    "temporarily out of stock",
    "notify me when available",
    "email when back in stock",
    "email me when in stock",
]

PRODUCTS = [
    {
        "name": "Meaco Cirro 12000 BTU (John Lewis)",
        "url": "https://www.johnlewis.com/meaco-cirro-12000-btu-super-quiet-smart-portable-air-conditioner-and-heater-white/p115462788",
    },
    {
        "name": "Meaco Cirro 14000 BTU Inverter (AO)",
        "url": "https://ao.com/product/acirro14kinv-meaco-cirro-air-conditioner-white-112209-825.aspx",
    },
    {
        "name": "Meaco MeacoCool 14kBTU Inverter (Currys)",
        "url": "https://www.currys.co.uk/products/meaco-meacocool-14kbtu-inverter-coolquiet-smart-air-conditioner-and-dehumidifier-white-10302001.html",
    },
]


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def check_product(page, url):
    """Returns True if the product looks IN STOCK, False if OUT OF STOCK."""
    page.goto(url, wait_until="networkidle", timeout=45000)
    # Give any lazy-loaded stock widgets a moment to render
    page.wait_for_timeout(3000)
    body_text = page.inner_text("body").lower()

    for phrase in OUT_OF_STOCK_PHRASES:
        if phrase in body_text:
            return False
    return True


def send_email(subject, body):
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipient = os.environ.get("TO_EMAIL", sender)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())


def main():
    state = load_state()
    any_change = False

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        )

        for product in PRODUCTS:
            name = product["name"]
            url = product["url"]
            try:
                in_stock = check_product(page, url)
                status = "IN STOCK" if in_stock else "out of stock"
                print(f"{name}: {status}")
            except Exception as e:
                print(f"{name}: ERROR checking page - {e}", file=sys.stderr)
                continue

            was_in_stock = state.get(name, {}).get("in_stock", False)

            if in_stock and not was_in_stock:
                # Just came back in stock - notify!
                send_email(
                    subject=f"Back in stock: {name}",
                    body=f"{name} is now showing as in stock.\n\n{url}",
                )
                any_change = True
                print(f"  -> Sent notification email for {name}")

            state[name] = {"in_stock": in_stock}

        browser.close()

    save_state(state)

    if any_change:
        print("At least one product changed to in-stock this run.")
    else:
        print("No changes this run.")


if __name__ == "__main__":
    main()
