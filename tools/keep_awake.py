"""Visit the Streamlit app; if it is asleep, press the wake-up button and wait until it runs."""
import re
import sys

from playwright.sync_api import sync_playwright

INDEX = open("index.html", encoding="utf-8").read()
URL = re.search(r'src="(https://[^"?]+\.streamlit\.app)', INDEX).group(1)

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(8_000)
    wake = page.get_by_role("button", name=re.compile("get this app back up", re.I))
    if wake.count():
        print("app was asleep: waking it up")
        wake.first.click()
        page.wait_for_timeout(90_000)
    else:
        print("app is awake")
    print("title:", page.title())
sys.exit(0)
