import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from datetime import datetime

URL = "https://arunahf.vercel.app/"
SCREENSHOT_DIR = "screenshots"

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="Browser to use: chrome, firefox, edge")
    parser.addoption("--mobile", action="store_true", help="Run in mobile viewport")
    parser.addoption("--headless", action="store_true", help="Run in headless mode")

@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser").lower()
    mobile = request.config.getoption("--mobile")
    headless = request.config.getoption("--headless")

    width, height = (375, 812) if mobile else (1280, 1000)

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_window_size(width, height)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    yield driver
    driver.quit()

@pytest.mark.usefixtures("driver")
def test_site(driver):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    driver.get(URL)
    time.sleep(3)  # wait for site to fully load

    # Check title
    assert "aruna" in driver.title.lower()
    print(f"✅ Page title validated: {driver.title}")

    # Test all buttons and .card-btn
    buttons = driver.find_elements(By.TAG_NAME, "button") + \
              driver.find_elements(By.CSS_SELECTOR, "a.card-btn, div.card-btn")

    for i, btn in enumerate(buttons):
        try:
            label = btn.text.strip() or btn.get_attribute("aria-label") or f"Button{i+1}"
            if btn.is_displayed() and btn.is_enabled():
                btn.screenshot(os.path.join(SCREENSHOT_DIR, f"btn_{i+1}_{label.replace(' ', '_')}.png"))
                btn.click()
                print(f"✅ Clicked button: {label}")
                time.sleep(0.5)
            else:
                print(f"⚠️ Skipped hidden/disabled button: {label}")
        except Exception as e:
            print(f"❌ Failed to click button {i+1}: {e}")

    # Test all links
    links = driver.find_elements(By.TAG_NAME, "a")
    for i, link in enumerate(links):
        href = link.get_attribute("href")
        if href and not href.startswith("javascript"):
            print(f"✅ Valid href: Link {i+1} → {href}")
        else:
            print(f"❌ Invalid href: Link {i+1}")

    # Try modal
    try:
        modal_candidates = driver.find_elements(By.CLASS_NAME, "modal-overlay")
        modal = next((m for m in modal_candidates if m.is_displayed()), None)

        if modal:
            print("✅ Modal appeared")

            modal_buttons = modal.find_elements(By.TAG_NAME, "button")
            for j, mbtn in enumerate(modal_buttons):
                if mbtn.is_displayed() and mbtn.is_enabled():
                    try:
                        label = mbtn.text.strip() or mbtn.get_attribute("aria-label") or f"ModalButton{j+1}"
                        mbtn.click()
                        print(f"✅ Clicked modal button: {label}")
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"❌ Failed to click modal button {j+1}: {e}")
        else:
            print("⚠️ Modal not visible")
    except Exception as e:
        print(f"⚠️ Modal interaction failed: {e}")
