from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def handle_cookies(page):
    """Accept cookies if the banner appears."""
    try:
        btn = page.locator("button#axeptio_btn_acceptAll")
        if btn.is_visible():
            btn.click()
            print("✅ Cookies accepted")
            page.locator("#axeptio_overlay").wait_for(state="hidden", timeout=5000)
    except TimeoutError:
        pass
    except Exception:
        pass


def safe_click(page, selector, timeout=5000):
    """Click an element, retrying after handling cookies if needed."""
    try:
        page.locator(selector).wait_for(state="visible", timeout=timeout)
        page.click(selector)
        return True
    except Exception as e:
        print(f"⚠️ Failed to click {selector} ({e}), retrying after handling cookies")
        handle_cookies(page)
        try:
            page.locator(selector).wait_for(state="visible", timeout=timeout)
            page.click(selector)
            return True
        except Exception as e2:
            print(f"❌ Cannot click {selector} after retry ({e2})")
            return False


def real_click(page, selector):
    """Physically simulate a click by moving the mouse to the element center."""
    element = page.locator(selector).first
    element.wait_for(state="visible", timeout=10000)
    box = element.bounding_box(timeout=10000)
    if not box:
        print(f"❌ Cannot get bounding box for {selector}")
        return False

    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2

    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.up()
    print(f"✅ Physical click simulated on {selector}")
    return True


def safe_goto(page, url):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except TimeoutError:
        print(f"⚠️ Timeout loading {url}, retrying...")
        handle_cookies(page)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)


def safe_fill(page, selector, value, timeout=5000):
    """Fill an input field, retrying after handling cookies if needed."""
    try:
        page.locator(selector).wait_for(state="visible", timeout=timeout)
        page.fill(selector, value)
        return True
    except Exception as e:
        print(f"⚠️ Failed to fill {selector} ({e}), retrying after handling cookies")
        handle_cookies(page)
        try:
            page.locator(selector).wait_for(state="visible", timeout=timeout)
            page.fill(selector, value)
            return True
        except Exception as e2:
            print(f"❌ Cannot fill {selector} after retry ({e2})")
            return False


def choose_ipssi(page):
    selector = "div[onclick*='form-organization-selection-939']"
    handle_cookies(page)

    if page.locator(selector).count() > 0:
        if safe_click(page, selector):
            print("✅ IPSSI selected")
        else:
            print("❌ Failed to select IPSSI")
    else:
        print("ℹ️ No IPSSI element to select")


def get_activity_hours(page):
    page.goto("https://general.global-exam.com", wait_until="domcontentloaded", timeout=60000)
    handle_cookies(page)

    time_block = page.locator(
        'div.flex.flex-col.items-center.gap-3.text-default-80:has(> p.w-2\\/3.text-center.leading-5:has-text("Temps d’activité")) > span.text-24'
    )

    if time_block.count() > 0 and time_block.first.is_visible(timeout=0):
        raw_time = time_block.first.inner_text().strip()
        hours_str = raw_time.split('h')[0].strip()
        hours = int(hours_str)
        print(f"⏱ Detected hours: {hours}")
        return hours
    else:
        print("ℹ️ No activity time found (instant read)")
        return 0


def loop_on_exercise(page):
    """Loop through exercises until the 'Replay Activity' button appears."""
    replay_selector = "button:has(span:has-text(\"Rejouer l'activité\"))"
    replay_locator = page.locator(replay_selector).first

    try:
        replay_locator.wait_for(state="visible", timeout=5000)
        print("✅ 'Replay Activity' button already visible, clicking and waiting")
        with page.expect_navigation(wait_until="networkidle"):
            replay_locator.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(500)
    except Exception as e:
        print(f"ℹ️ 'Replay Activity' button not visible initially ({e}), starting loop")

    while not replay_locator.is_visible():
        solve_question(page)

    print("🎉 'Replay Activity' button detected, loop finished.")


def click_passer_continuer(page, timeout=5000):
    """Click 'Skip' or 'Continue' button if it appears."""
    passer_selector = "button:has(span:has-text('Passer'))"
    continuer_selector = "button:has(span:has-text('Continuer'))"
    suivant_selector = "button:has(span:has-text('Suivant'))"
    terminer_selector = "button:has(span:has-text('Terminer'))"

    try:
        page.wait_for_selector(f"{passer_selector}, {continuer_selector}, {suivant_selector}, {terminer_selector}", state="visible", timeout=timeout)
    except Exception:
        print("ℹ️ No 'Skip' or 'Continue' button visible in time")
        return

    if page.locator(passer_selector).first.is_visible():
        print("✅ 'Skip' button visible, clicking")
        try:
            page.locator(passer_selector).first.click(force=True, timeout=timeout, no_wait_after=True)
            return
        except Exception as e:
            print(f"⚠️ Failed to click 'Skip' ({e})")

    elif page.locator(continuer_selector).first.is_visible():
        print("✅ 'Continue' button visible, clicking")
        try:
            page.locator(continuer_selector).first.click(force=True, timeout=timeout, no_wait_after=True)
            return
        except Exception as e:
            print(f"⚠️ Failed to click 'Continue' ({e})")

    elif page.locator(suivant_selector).first.is_visible():
        print("✅ 'Next' button visible, clicking")
        try:
            page.locator(suivant_selector).first.click(force=True, timeout=timeout, no_wait_after=True)
            return
        except Exception as e:
            print(f"⚠️ Failed to click 'Next' ({e})")
    elif page.locator(terminer_selector).first.is_visible():
        print("✅ 'Finish' button visible, clicking")
        try:
            page.locator(terminer_selector).first.click(force=True, timeout=timeout, no_wait_after=True)
            return
        except Exception as e:
            print(f"⚠️ Failed to click 'Finish' ({e})")

def click_valider(page):
    valider_selector = "button:has(span:has-text('Valider'))"

    if page.locator(valider_selector).first.is_visible():
        print("✅ 'Validate' button visible, clicking")
        try:
            page.locator(valider_selector).first.click(force=True)
            return
        except Exception as e:
            print(f"⚠️ Failed to click 'Validate' ({e})")
    else:
        print("ℹ️ No 'Skip', 'Continue', or 'Validate' button visible")


def solve_question(page):
    actions = [
        ("click", "Why was Susan invited to a web conference with Tammy?", ["label:has-text('For the induction program of new recruits.')"], ""),
        ("click", "What are the advantages of implementing iT in businesses?", [
            "label:has-text('Companies can automate manual processes.')",
            "label:has-text('It is cost-effective in the long run.')"], ""),
        ("click", "Fill in the blanks with the following words: sensor, Integrated Chip (IC)", [
            "button:has-text('Integrated Chip (IC)')",
            "button:has-text('sensor')"], ""),
        ("click", "Place the words in the correct order to form a question:", [
            "button:has-text('Could you please')",
            "button:has-text('enlighten me')",
            "button:has-text('with more benefits of  IT')",
            "button:has-text('?')"], ""),
        ("fill", "Fill-in-the-blank with a word that means: “support”, “assistance”", ['[data-name="user-answer-container"]'], "helping"),
        ("click", "Match the beginnings of the sentences with the endings:", [
            "button:has-text('a robotic arm.')",
            "button:has-text('some more advantages of the IT sector.')",
            "button:has-text('assistant system engineer recently.')"], ""),
        ("click", "What was the name of the webinar conducted by Brian?", ["label:has-text('Introduction to Key fields in IT.')"], ""),
        ("click", "Place the words in the correct order to form a question:", [
            "button:has-text('this takes')",
            "button:has-text('us to the')",
            "button:has-text('next important field:')",
            "button:has-text('machine learning')"], ""),
        ("click", "Match the phrase with the correct meaning:", [
            "button:has-text('Improves the learning experience of machines.')",
            "button:has-text('Starting point.')",
            "button:has-text('Where a user interacts with a system.')"], ""),
        ("fill", "Question Fill in the blank with a word that means: protect or safeguard", ['[data-name="user-answer-container"]'], "defend"),
        ("click", "Fill in the blank with the following words: accuracy, improves.", [
            "button:has-text('improves')",
            "button:has-text('accuracy')"], ""),
        ("click", "Which are the critical fields used by ESS?", [
            "label:has-text('Al')",
            "label:has-text('ML')",
            "label:has-text('Cyber Security')"], ""),
        ("click", "Using the vocabulary you have just learned, fill in the blanks with the missing words.", [
            "button:has-text('confused')",
            "button:has-text('algorithms')",
            "button:has-text('Training data')",
            "button:has-text('programming')",
            "button:has-text('improves')"], ""),
    ]

    handle_cookies(page)
    question_selector = "h2.relative span[aria-hidden='false']"

    try:
        page.locator(question_selector).first.wait_for(state="visible", timeout=2000)
        question = page.locator(question_selector).first.inner_text().strip()
        print(f"ℹ️ Detected question: {question}")
    except Exception:
        print("⚠️ No question detected in time, trying skip/continue")
        click_passer_continuer(page)
        return

    for action, label, selectors, value in actions:
        if label in question:
            print(f"✅ Question matched: {label}")

            if action == "click":
                try:
                    for selector in selectors:
                        real_click(page, selector)
                        page.wait_for_timeout(5000)
                        print(f"✅ Clicked selector '{selector}'")
                    click_valider(page)
                    click_passer_continuer(page)
                    break
                except Exception as e:
                    print(f"⚠️ Failed to click answer '{label}' ({e})")

            elif action == "fill":
                try:
                    for selector in selectors:
                        locator = page.locator(selector).first
                        locator.wait_for(state="visible", timeout=5000)
                        locator.click()
                        locator.fill(value)
                        print(f"✅ Filled selector '{selector}'")
                    click_valider(page)
                    click_passer_continuer(page)
                    break
                except Exception as e:
                    print(f"⚠️ Failed to fill answer '{label}' ({e})")
    else:
        print(f"ℹ️ Question not found in list: {question}, moving on")
        click_passer_continuer(page)


def go_to_exercise(page):
    safe_goto(page, "https://general.global-exam.com/certificates")
    handle_cookies(page)

    safe_click(page, "div.card.cursor-pointer:has-text('IT & Cybersécurité')")

    it_everywhere_selector = "div.group.cursor-pointer:has-text('IT is everywhere')"

    if not page.locator(it_everywhere_selector).is_visible():
        print("ℹ️ 'IT is everywhere' module not visible")
    else:
        print("✅ 'IT is everywhere' module visible")

    safe_click(page, it_everywhere_selector)
    page.wait_for_load_state("domcontentloaded")


# -------------------------------
#  Main Script
# -------------------------------

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()

    page.goto("https://auth.global-exam.com/login")
    page.wait_for_load_state("load")
    handle_cookies(page)

    safe_fill(page, "[name='email']", EMAIL)
    safe_fill(page, "[name='password']", PASSWORD)
    safe_click(page, "button[type='submit']")

    choose_ipssi(page)

    while get_activity_hours(page) < 20:
        go_to_exercise(page)
        loop_on_exercise(page)

    page.wait_for_timeout(5000)
    browser.close()
