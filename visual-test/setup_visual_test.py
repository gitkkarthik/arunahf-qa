import os

BASE = os.path.dirname(os.path.abspath(__file__))

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

# --- Files to create ---

requirements = """
selenium>=4.19.0
webdriver-manager>=4.0.1
pillow>=10.3.0
pytest>=8.4.1
pytest-html>=4.1.1
imageio>=2.34.0
"""

dev_requirements = """
flake8>=6.1.0
black>=24.4.0
isort>=5.13.2
pre-commit>=3.7.0
"""

run_sh = """
#!/bin/bash

echo "🔄 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "🧪 Running visual regression tests..."
pytest tests/ --html=test-report.html --self-contained-html

REPORT_PATH="test-report.html"
if [ -f "$REPORT_PATH" ]; then
    echo "📂 Opening test report..."
    if command -v xdg-open > /dev/null; then
        xdg-open "$REPORT_PATH"
    elif command -v open > /dev/null; then
        open "$REPORT_PATH"
    else
        echo "⚠️ Can't automatically open report. Please open $REPORT_PATH manually."
    fi
else
    echo "❌ Test report not found."
fi
"""

run_bat = """
@echo off
echo 🔄 Installing requirements...
pip install -r requirements.txt

echo 🧪 Running visual regression tests...
pytest tests/ --html=test-report.html --self-contained-html

echo 📂 Opening test report...
start test-report.html
"""

# --- Create output files ---
write_file(os.path.join(BASE, "requirements.txt"), requirements)
write_file(os.path.join(BASE, "requirements-dev.txt"), dev_requirements)
write_file(os.path.join(BASE, "run_tests.sh"), run_sh)
write_file(os.path.join(BASE, "run_tests.bat"), run_bat)

print("\n🎉 All setup files created! You can now run:\n")
print("📦 install:   pip install -r requirements.txt")
print("🚀 test:      ./run_tests.bat   (Windows) or ./run_tests.sh (Mac/Linux)")
