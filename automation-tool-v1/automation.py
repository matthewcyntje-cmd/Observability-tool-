import csv
import time
from playwright.sync_api import sync_playwright

QUERIES_FILE = "/Users/matthewcyntje/Automation Tool/automation-tool-v1/Test 3 - Sheet1.csv"
OUTPUT_FILE = "/Users/matthewcyntje/Automation Tool/automation-tool-v1/responses.csv"
PROJECT_URL = "https://chatgpt.com/g/g-p-6a44028832d081918fbf3781b0b289d5-test-3/project"
SENTINEL = "RESPONSEHASENDED"

def load_queries():
    queries = []
    with open(QUERIES_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for i, row in enumerate(reader):
            if row and row[0].strip():
                queries.append({
                    "index": i + 1,
                    "text": row[0].strip()
                })
    return queries

def run_automation():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]

        queries = load_queries()
        print(f"Loaded {len(queries)} queries")

        # Set up output CSV
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Query", "Response"])

        for query in queries:
            print(f"\n--- Query {query['index']}: {query['text']} ---")

            chatgpt_page = context.new_page()
            chatgpt_page.set_viewport_size({"width": 1920, "height": 1080})
            chatgpt_page.goto(PROJECT_URL)
            chatgpt_page.wait_for_load_state("networkidle")
            time.sleep(4)

            # Submit query
            try:
                textarea = chatgpt_page.locator("#prompt-textarea").first
                textarea.click()
                time.sleep(1)
                textarea.fill(query['text'])
                time.sleep(0.5)
                chatgpt_page.keyboard.press("Enter")
                print("Query submitted, waiting for response...")
            except Exception as e:
                print(f"Could not submit query: {e}")
                chatgpt_page.close()
                continue

            # Wait for RESPONSEHASENDED
            max_wait = 180
            start_time = time.time()
            response_text = None

            while time.time() - start_time < max_wait:
                try:
                    page_content = chatgpt_page.inner_text("body")
                    if SENTINEL in page_content:
                        messages = chatgpt_page.locator("[data-message-author-role='assistant']").all()
                        if messages:
                            last_message = messages[-1].inner_text()
                            response_text = last_message.replace(SENTINEL, "").strip()
                            print(f"Response captured ({len(response_text)} chars)")
                        break
                except:
                    pass
                time.sleep(3)

            if not response_text:
                print(f"Timeout on query {query['index']}, skipping")
                chatgpt_page.close()
                continue

            # Write to CSV immediately after each response
            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([query['text'], response_text])
            print(f"Written to CSV: query {query['index']}")

            chatgpt_page.close()
            time.sleep(2)

        print("\nAll queries complete! Check responses.csv")

run_automation()