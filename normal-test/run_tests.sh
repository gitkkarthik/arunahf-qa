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