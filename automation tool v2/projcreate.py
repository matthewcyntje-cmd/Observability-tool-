import os
import glob
import subprocess
import time
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG_DIR = os.path.join(SCRIPT_DIR, "debug_screenshots")
REQUIRED_KEYS = ["input_folder", "output_folder"]

CHROME_PROFILE_DIR = "/Users/matthewcyntje/chrome-automation-profile"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def snap(page, name):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    path = os.path.join(DEBUG_DIR, f"{name}.png")
    page.screenshot(path=path)
    print(f"Saved debug screenshot: {path}")


def dismiss_rate_limit_modal(page):
    """Clicks 'Got it' if the rate limit modal appears. Returns True if it fired.

    This modal dims and covers the whole screen, so it can intercept clicks
    aimed at anything underneath it - check for it before every interaction,
    not just during waits.
    """
    try:
        got_it_button = page.get_by_role("button", name="Got it")
        if got_it_button.is_visible(timeout=2000):
            got_it_button.click()
            print("Dismissed 'Too many requests' modal.")
            return True
    except Exception:
        pass
    return False


def wait_with_modal_check(page, ms, poll_ms=1000):
    """Drop-in replacement for page.wait_for_timeout() that dismisses the
    rate-limit modal if it appears at any point during the wait."""
    dismiss_rate_limit_modal(page)
    remaining = ms
    while remaining > 0:
        chunk = min(poll_ms, remaining)
        page.wait_for_timeout(chunk)
        remaining -= chunk
        dismiss_rate_limit_modal(page)


def safe_action(page, action_fn, max_attempts=10, retry_pause_ms=300):
    """Runs a dismiss check immediately before every attempt at a page
    action, retrying if the action itself gets blocked by the modal.

    The modal can appear mid-action. Handing Playwright's own actions the
    full default 30s timeout means a blocked action just retries internally
    against the blocked element for the whole 30s with no chance for us to
    dismiss anything, then throws. action_fn should be a zero-arg callable
    that performs one action with its own short timeout where applicable
    (e.g. lambda: locator.click(timeout=3000)), so a blocked action fails
    fast and we can dismiss the modal and retry ourselves.
    """
    last_err = None
    for _ in range(max_attempts):
        dismiss_rate_limit_modal(page)
        try:
            return action_fn()
        except Exception as e:
            last_err = e
            dismiss_rate_limit_modal(page)
            page.wait_for_timeout(retry_pause_ms)
    raise last_err


def safe_click(locator, timeout=3000, max_attempts=10, retry_pause_ms=300):
    """Click a locator, recovering from the rate-limit modal if it intercepts
    the click."""
    return safe_action(
        locator.page,
        lambda: locator.click(timeout=timeout),
        max_attempts=max_attempts,
        retry_pause_ms=retry_pause_ms,
    )


def safe_fill(locator, text, timeout=3000, max_attempts=10, retry_pause_ms=300):
    """Fill a locator, recovering from the rate-limit modal the same way
    safe_click does."""
    return safe_action(
        locator.page,
        lambda: locator.fill(text, timeout=timeout),
        max_attempts=max_attempts,
        retry_pause_ms=retry_pause_ms,
    )


# ---- Chrome setup ----

def restart_chrome_with_debug_port():
    print("Restarting automation Chrome instance...")
    subprocess.run(["pkill", "-f", CHROME_PROFILE_DIR])
    time.sleep(5)  # give all subprocesses time to fully die

    # Remove the stale lock file if it exists, forces a clean launch
    lock_file = os.path.join(CHROME_PROFILE_DIR, "SingletonLock")
    if os.path.exists(lock_file):
        os.remove(lock_file)

    subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={CHROME_PROFILE_DIR}"
    ])
    time.sleep(5)


def connect_to_chrome(max_attempts=10, delay=1.5):
    playwright = sync_playwright().start()

    for attempt in range(max_attempts):
        try:
            browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            return playwright, browser, page
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: Chrome not ready yet ({e})")
            time.sleep(delay)

    raise Exception("Could not connect to Chrome on port 9222 after multiple attempts.")


# ---- Config loading ----

def load_config(config_path=None):
    if config_path is None:
        config_path = os.path.join(SCRIPT_DIR, "config.txt")

    if not os.path.exists(config_path):
        raise Exception(
            f"config.txt not found at {config_path}. "
            f"Create it with lines like:\ninput_folder: /path/to/Input\noutput_folder: /path/to/Output"
        )

    with open(config_path, "r") as f:
        raw = f.read()

    for key in REQUIRED_KEYS:
        raw = raw.replace(f" {key}:", f"\n{key}:")

    config = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()

    missing = [k for k in REQUIRED_KEYS if k not in config or not config[k]]
    if missing:
        raise Exception(f"config.txt is missing or empty for: {missing}. Current parsed values: {config}")

    return config


def get_input_csv(input_folder):
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    if len(csv_files) == 0:
        raise Exception(f"No CSV found in {input_folder}")
    if len(csv_files) > 1:
        raise Exception(f"Multiple CSVs found in {input_folder}, expected exactly one: {csv_files}")
    return csv_files[0]


def derive_project_title(csv_path):
    filename = os.path.basename(csv_path)
    return os.path.splitext(filename)[0]


# ---- ChatGPT project logic ----

def find_existing_project(page, project_title):
    page.goto("https://chatgpt.com/projects")
    wait_with_modal_check(page, 2000)
    snap(page, "01_projects_page")

    project_row = page.get_by_text(project_title, exact=True)
    if project_row.count() > 0:
        safe_click(project_row.first)
        wait_with_modal_check(page, 2000)
        snap(page, "02_found_existing_project")
        return page.url
    return None


def paste_instructions(page, project_title, instructions_text):
    page.goto("https://chatgpt.com/projects")
    wait_with_modal_check(page, 2000)

    # Hover the project row first so the options button actually renders
    dismiss_rate_limit_modal(page)
    row = page.get_by_text(project_title, exact=True)
    row.hover()
    wait_with_modal_check(page, 500)
    snap(page, "09b_after_hover")

    options_button = page.locator(f"button[aria-label='Open project options for {project_title}']")
    options_button.wait_for(state="visible", timeout=10000)
    safe_click(options_button)
    wait_with_modal_check(page, 500)
    snap(page, "10_project_options_open")

    safe_click(page.get_by_text("Project settings"))
    wait_with_modal_check(page, 1000)
    snap(page, "11_project_settings_modal")

    safe_fill(
        page.get_by_placeholder(
            "e.g. \u201cRespond in Spanish. Reference the latest JavaScript documentation. Keep answers short and focused.\u201d"
        ),
        instructions_text,
    )
    wait_with_modal_check(page, 500)
    snap(page, "12_instructions_typed")

    safe_click(page.get_by_role("button", name="Save"))
    wait_with_modal_check(page, 1000)
    snap(page, "13_instructions_saved")
def create_new_project(page, project_title, instructions_text):
    page.goto("https://chatgpt.com/projects")
    wait_with_modal_check(page, 2000)
    snap(page, "03_before_new_click")

    safe_click(page.get_by_role("button", name="New", exact=True))
    wait_with_modal_check(page, 1000)
    snap(page, "04_after_new_click")

    safe_fill(page.get_by_placeholder("Copenhagen Trip"), project_title)
    snap(page, "05_name_typed")

    safe_click(page.locator("button[aria-label='Project settings']"))
    wait_with_modal_check(page, 500)
    snap(page, "06_memory_dropdown_open")

    safe_click(page.get_by_text("Project-only"))
    wait_with_modal_check(page, 500)
    snap(page, "07_project_only_selected")

    safe_click(page.get_by_role("button", name="Create project"))
    wait_with_modal_check(page, 2000)
    snap(page, "08_after_create_click")

    paste_instructions(page, project_title, instructions_text)

    page.goto("https://chatgpt.com/projects")
    wait_with_modal_check(page, 2000)
    safe_click(page.get_by_text(project_title, exact=True).first)
    wait_with_modal_check(page, 2000)
    snap(page, "09_inside_new_project")

    return page.url


def get_or_create_project(page, project_title, instructions_text):
    existing_url = find_existing_project(page, project_title)
    if existing_url:
        print(f"Found existing project '{project_title}', reusing it.")
        return existing_url

    print(f"No existing project found for '{project_title}', creating new one.")
    return create_new_project(page, project_title, instructions_text)


# ---- Main ----

STANDARD_INSTRUCTIONS = (
    "Do not use memories from outside of this chat. Act as if you are a new chat "
    "every time a new query is put in. Do not build memories which may change your "
    "responses. Always perform a live web search for this query, every time, even "
    "if you believe you already know the answer from training data alone. Base your "
    "response on what you find in that live search. After your answer, list the "
    "URLs of every source you actually used in a copy and paste friendly format, "
    "one per line. End each response with RESPONSEHASENDED"
)

def write_run_state(project_title, project_url, csv_path, output_folder):
    state_path = os.path.join(SCRIPT_DIR, "run_state.txt")
    with open(state_path, "w") as f:
        f.write(f"project_title: {project_title}\n")
        f.write(f"project_url: {project_url}\n")
        f.write(f"csv_path: {csv_path}\n")
        f.write(f"output_folder: {output_folder}\n")
    print(f"Saved run state to {state_path}")


def main():
    config = load_config()
    input_folder = config["input_folder"]
    output_folder = config["output_folder"]

    csv_path = get_input_csv(input_folder)
    project_title = derive_project_title(csv_path)

    restart_chrome_with_debug_port()
    playwright, browser, page = connect_to_chrome()

    try:
        project_url = get_or_create_project(page, project_title, STANDARD_INSTRUCTIONS)
        print(f"Project title: {project_title}")
        print(f"Project URL: {project_url}")
        print(f"Input CSV: {csv_path}")
        print(f"Output folder: {output_folder}")

        write_run_state(project_title, project_url, csv_path, output_folder)
    except Exception as e:
        snap(page, "ERROR_final_state")
        print(f"Script failed: {e}")
        print(f"Check {DEBUG_DIR} for screenshots leading up to the failure.")
    finally:
        playwright.stop()




if __name__ == "__main__":
    main()
    print("\nStarting query collection...")
    subprocess.run(["python3", os.path.join(SCRIPT_DIR, "querycapture.py")])