import os
import csv
import time
import subprocess
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SENTINEL = "RESPONSEHASENDED"
QUERY_DELAY_SECONDS = 15


def minimize_chrome():
    subprocess.run([
        "osascript", "-e",
        'tell application "Google Chrome" to set miniaturized of window 1 to true'
    ])


def load_run_state():
    state_path = os.path.join(SCRIPT_DIR, "run_state.txt")
    if not os.path.exists(state_path):
        raise Exception(
            f"run_state.txt not found at {state_path}. Run projcreate.py first."
        )

    state = {}
    with open(state_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            state[key.strip()] = value.strip()

    required = ["project_title", "project_url", "csv_path", "output_folder"]
    missing = [k for k in required if k not in state or not state[k]]
    if missing:
        raise Exception(f"run_state.txt is missing: {missing}")

    return state


def build_output_path(csv_path, output_folder):
    filename = os.path.basename(csv_path)
    base = os.path.splitext(filename)[0]
    return os.path.join(output_folder, f"{base}_output.csv")


def load_queries(csv_path):
    queries = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for i, row in enumerate(reader):
            if row and row[0].strip():
                queries.append({
                    "index": i + 1,
                    "text": row[0].strip()
                })
    return queries


def start_new_chat(page, project_title):
    """Return to the project's fresh compose view without reloading the page.

    The breadcrumb link back to the project only renders while inside an
    active conversation; if we're already at the project's empty compose
    view, there's nothing to click.
    """
    new_chat_link = page.get_by_role("link", name=f"Open {project_title} project")
    if new_chat_link.count() > 0:
        new_chat_link.first.click()
        page.wait_for_timeout(1000)


def run_automation():
    run_start_time = time.time()

    state = load_run_state()
    project_title = state["project_title"]
    project_url = state["project_url"]
    csv_path = state["csv_path"]
    output_folder = state["output_folder"]
    output_file = build_output_path(csv_path, output_folder)

    os.makedirs(output_folder, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]

        queries = load_queries(csv_path)
        print(f"Loaded {len(queries)} queries")
        print(f"Using project: {project_url}")
        print(f"Writing output to: {output_file}")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Query", "Response"])

        all_succeeded = True

        chatgpt_page = context.new_page()
        chatgpt_page.set_viewport_size({"width": 1920, "height": 1080})
        minimize_chrome()
        chatgpt_page.goto(project_url)
        chatgpt_page.wait_for_load_state("networkidle")
        time.sleep(4)

        for query in queries:
            print(f"\n--- Query {query['index']}: {query['text']} ---")

            MAX_RETRIES = 3
            response_text = None
            attempt = 1

            while attempt <= MAX_RETRIES and response_text is None:
                print(f"Attempt {attempt}/{MAX_RETRIES} for query {query['index']}")

                try:
                    start_new_chat(chatgpt_page, project_title)

                    textarea = chatgpt_page.locator("#prompt-textarea").first
                    textarea.click()
                    time.sleep(1)
                    textarea.fill(query['text'])
                    time.sleep(0.5)
                    chatgpt_page.keyboard.press("Enter")
                    print("Query submitted, waiting for response...")

                    max_wait = 180
                    start_time = time.time()

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

                except Exception as e:
                    print(f"Attempt {attempt} failed to submit or capture: {e}")

                if response_text is None:
                    print(f"No response within {max_wait}s on attempt {attempt}, starting a new chat and retrying...")
                    attempt += 1
                    time.sleep(2)

            start_new_chat(chatgpt_page, project_title)

            if not response_text:
                print(f"Query {query['index']} failed after {MAX_RETRIES} attempts, skipping")
                all_succeeded = False
                continue

            with open(output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([query['text'], response_text])
            print(f"Written to CSV: query {query['index']}")

            time.sleep(QUERY_DELAY_SECONDS)

        chatgpt_page.close()

        run_end_time = time.time()
        elapsed_seconds = run_end_time - run_start_time
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        elapsed_str = f"{minutes}m {seconds}s"

        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([])
            writer.writerow(["Total run time", elapsed_str])

        print(f"\nAll queries complete! Check {output_file}")
        print(f"Total run time: {elapsed_str}")

        if all_succeeded:
            os.remove(csv_path)
            print(f"Deleted input CSV: {csv_path}")
        else:
            print("Some queries failed or timed out, input CSV was NOT deleted so you can retry.")


if __name__ == "__main__":
    run_automation()