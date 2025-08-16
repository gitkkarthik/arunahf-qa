import os
import time
import imageio
from PIL import Image, ImageChops
import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

URL = "https://arunahf.vercel.app/"
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
BASE_DIR = os.path.join("screenshots", timestamp)
BASELINE_DIR = os.path.join(BASE_DIR, "baseline")
CURRENT_DIR = os.path.join(BASE_DIR, "current")
FAILED_DIR = os.path.join(BASE_DIR, "failed")
GIF_DIR = os.path.join(BASE_DIR, "scroll_gifs")
for d in [BASELINE_DIR, CURRENT_DIR, FAILED_DIR, GIF_DIR]:
    os.makedirs(d, exist_ok=True)

MOBILE_VIEWPORTS = {
    "iPhone X": (375, 812),
    "Galaxy S20": (360, 800),
    "Desktop": (1280, 1000)
}

def get_latest_baseline_dir():
    parent = "screenshots"
    dirs = sorted([d for d in os.listdir(parent) if os.path.isdir(os.path.join(parent, d))], reverse=True)
    for d in dirs:
        path = os.path.join(parent, d, "baseline")
        if os.path.exists(path):
            return path
    return BASELINE_DIR

def compare_images(baseline_path, current_path, diff_path):
    baseline = Image.open(baseline_path)
    current = Image.open(current_path)
    diff = ImageChops.difference(baseline, current)
    if diff.getbbox():
        diff.save(diff_path)
        return False
    return True

def save_and_compare(name, driver, request):
    current = os.path.join(CURRENT_DIR, f"{name}.png")
    baseline = os.path.join(get_latest_baseline_dir(), f"{name}.png")
    diff = os.path.join(FAILED_DIR, f"{name}_diff.png")
    driver.save_screenshot(current)

    if not os.path.exists(baseline):
        Image.open(current).save(baseline)
        print(f"📸 Saved new baseline: {name}")
    else:
        passed = compare_images(baseline, current, diff)
        if not passed:
            html = f"""<div><b>{name}</b><table>
              <tr><th>Baseline</th><th>Current</th><th>Diff</th></tr><tr>
              <td><img src="file:///{baseline}" height="150"/></td>
              <td><img src="file:///{current}" height="150"/></td>
              <td><img src="file:///{diff}" height="150"/></td>
              </tr></table></div>"""
            request.node.extra = getattr(request.node, "extra", [])
            request.node.extra.append(pytest_html.extras.html(html))
            pytest.fail(f"❌ Visual diff found: {name}")

def capture_scroll_screens(driver, name_prefix, request):
    screenshots = []
    for i in range(10):
        scroll_position = driver.execute_script("return window.scrollY + window.innerHeight")
        max_scroll = driver.execute_script("return document.body.scrollHeight")
        filename = os.path.join(CURRENT_DIR, f"{name_prefix}_scroll_{i}.png")
        driver.save_screenshot(filename)
        screenshots.append(filename)
        save_and_compare(f"{name_prefix}_scroll_{i}", driver, request)
        if scroll_position >= max_scroll:
            break
        driver.execute_script("window.scrollBy(0, window.innerHeight)")
        time.sleep(1)
    return screenshots

def create_gif(images, output_path):
    imageio.mimsave(output_path, [Image.open(img) for img in images], fps=1)

def get_driver(browser_name, headless):
    if browser_name == "chrome":
        options = ChromeOptions()
        if headless: options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,1000")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        if headless: options.add_argument("--headless")
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    elif browser_name == "edge":
        options = EdgeOptions()
        if headless: options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,1000")
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    raise ValueError(f"Unsupported browser: {browser_name}")

def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="Run headless mode")

BROWSERS = ["chrome"]
VIEWPORTS = ["Desktop", "iPhone X", "Galaxy S20"]

@pytest.mark.parametrize("browser_name", BROWSERS)
@pytest.mark.parametrize("viewport_label", VIEWPORTS)
def test_full_visual_and_functional(browser_name, viewport_label, request):
    headless = request.config.getoption("--headless")
    driver = get_driver(browser_name, headless)
    width, height = MOBILE_VIEWPORTS[viewport_label]

    try:
        driver.set_window_size(width, height)
        driver.get(URL)
        time.sleep(3)

        prefix = f"{browser_name}_{viewport_label.replace(' ', '_')}"

        save_and_compare(f"{prefix}_hero", driver, request)

        scroll_imgs = capture_scroll_screens(driver, prefix, request)
        gif_path = os.path.join(GIF_DIR, f"{prefix}_scroll.gif")
        create_gif(scroll_imgs, gif_path)

        request.node.extra = getattr(request.node, "extra", [])
        request.node.extra.append(pytest_html.extras.html(
            f"<div><b>🌀 Scroll GIF:</b><br/><img src='file:///{gif_path}' height='300'/></div>"
        ))

        # Functional checks
        print("\n🔎 Button test started:")
        buttons = driver.find_elements(By.TAG_NAME, "button") + driver.find_elements(By.CLASS_NAME, "card-btn")
        for i, btn in enumerate(buttons):
            try:
                label = btn.text or btn.get_attribute("aria-label") or f"Button{i+1}"
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    print(f"✅ Clicked button: {label}")
                    time.sleep(0.5)
                else:
                    print(f"⚠️ Skipped (hidden/disabled): {label}")
            except Exception as e:
                print(f"❌ Failed to click button {i+1}: {e}")

        print("\n🔗 Link check started:")
        links = driver.find_elements(By.TAG_NAME, "a")
        for i, link in enumerate(links):
            href = link.get_attribute("href")
            if href and not href.startswith("javascript"):
                print(f"✅ Valid href: Link {i+1} → {href}")
            else:
                print(f"❌ Invalid href: Link {i+1}")

        # Modal interaction
        try:
            modal = driver.find_element(By.CLASS_NAME, "modal-overlay")
            if modal.is_displayed():
                print("✅ Modal appeared")

                modal_buttons = modal.find_elements(By.TAG_NAME, "button")
                for j, mbtn in enumerate(modal_buttons):
                    if mbtn.is_displayed() and mbtn.is_enabled():
                        try:
                            mbtn.click()
                            print(f"✅ Clicked modal button {j+1}")
                            time.sleep(0.5)
                        except:
                            print(f"❌ Modal button {j+1} click failed")
        except Exception as e:
            print(f"⚠️ Modal not found or interaction failed: {e}")

    finally:
        driver.quit()
