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
# ... (rest of your imports and directories remain unchanged)

URL = "https://arunahf.vercel.app/"

BASELINE_DIR = "screenshots/baseline"
CURRENT_DIR = "screenshots/current"
FAILED_DIR = "screenshots/failed"
GIF_DIR = "screenshots/scroll_gifs"
os.makedirs(BASELINE_DIR, exist_ok=True)
os.makedirs(CURRENT_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)
os.makedirs(GIF_DIR, exist_ok=True)

MOBILE_VIEWPORTS = {
    "iPhone X": (375, 812),
    "Galaxy S20": (360, 800),
    "Desktop": (1280, 1000)
}

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
    baseline = os.path.join(BASELINE_DIR, f"{name}.png")
    diff = os.path.join(FAILED_DIR, f"{name}_diff.png")
    driver.save_screenshot(current)

    if not os.path.exists(baseline):
        Image.open(current).save(baseline)
        print(f"📸 Saved baseline: {name}")
    else:
        passed = compare_images(baseline, current, diff)
        if not passed:
            html_snippet = f"""
            <div><b>{name}</b>
            <table>
              <tr><th>Baseline</th><th>Current</th><th>Diff</th></tr>
              <tr>
                <td><img src="file:///{baseline}" height="150"/></td>
                <td><img src="file:///{current}" height="150"/></td>
                <td><img src="file:///{diff}" height="150"/></td>
              </tr>
            </table></div>"""
            request.node.extra = getattr(request.node, "extra", [])
            request.node.extra.append(pytest_html.extras.html(html_snippet))
            pytest.fail(f"❌ Visual diff in {name}")

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

def create_gif(screenshot_files, output_path):
    images = [Image.open(img) for img in screenshot_files]
    imageio.mimsave(output_path, images, fps=1)

@pytest.mark.parametrize("browser_name", ["chrome"])
@pytest.mark.parametrize("viewport_label", list(MOBILE_VIEWPORTS.keys()))

def get_driver(browser_name: str, headless: bool):
    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,1000")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif browser_name == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    elif browser_name == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,1000")
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

BROWSERS = ["chrome", "firefox", "edge"]
VIEWPORTS = ["Desktop", "iPhone X", "Galaxy S20"]

@pytest.mark.parametrize("browser_name", BROWSERS)
@pytest.mark.parametrize("viewport_label", VIEWPORTS)
def test_full_flow(browser_name, viewport_label, request):
    headless_env = os.getenv("HEADLESS", "false").lower() == "true"
    headless_cli = request.config.getoption("--headless")
    headless = headless_env or headless_cli

    driver = get_driver(browser_name, headless)

    driver = None
    width, height = MOBILE_VIEWPORTS[viewport_label]
    try:
        if browser_name == "chrome":
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        elif browser_name == "firefox":
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        elif browser_name == "edge":
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

        driver.set_window_size(width, height)
        driver.get(URL)
        time.sleep(3)

        # Hero Screenshot
        name_prefix = f"{browser_name}_{viewport_label.replace(' ', '_')}"
        save_and_compare(f"{name_prefix}_hero", driver, request)

        # Scroll screenshots
        scroll_imgs = capture_scroll_screens(driver, name_prefix, request)
        gif_path = os.path.join(GIF_DIR, f"{name_prefix}_scroll.gif")
        create_gif(scroll_imgs, gif_path)
        if os.path.exists(gif_path):
            request.node.extra = getattr(request.node, "extra", [])
            request.node.extra.append(pytest_html.extras.html(
                f"<div><b>🌀 Scroll Summary GIF:</b><br/><img src='file:///{gif_path}' height='300'/></div>"
            ))

        # Modal interaction
        try:
            button = driver.find_element(By.XPATH, "//button[contains(., 'Get Started') or contains(., 'Join')]")
            button.click()
            time.sleep(2)

            save_and_compare(f"{name_prefix}_modal_top", driver, request)

            modal = driver.find_element(By.XPATH, "//div[contains(@class,'modal')]")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 2", modal)
            time.sleep(1)
            save_and_compare(f"{name_prefix}_modal_scrolled", driver, request)

            close_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label,'Close') or contains(text(),'×')]")
            close_btn.click()
        except Exception as e:
            print(f"⚠️ Modal interaction failed: {e}")

    finally:
        if driver:
            driver.quit()
