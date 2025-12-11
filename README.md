# 📘 How to Run the Combined Visual and Functional Tests


## ✅ Install Dependencies

```bash
cd visual-test
pip install -r requirements.txt
```

---

## 🚀 Running Tests

### ▶️ Headless Mode (no browser UI)

```bash
pytest --headless --html=report.html --self-contained-html
```

This is useful for CI/CD environments or automated pipelines.

---

### ▶️ With Browser UI (headed mode)

```bash
pytest --html=report.html --self-contained-html
```

This allows you to see browser activity during testing.

---

## 🛠️ Customize Run

You can filter by browser or test name:

```bash
pytest -k "chrome" --html=chrome-only-report.html --self-contained-html
```

You can also use:

- `-n auto` to run tests in parallel if `pytest-xdist` is installed.
- `--capture=tee-sys` to see both CLI and HTML report logs.

---

## 🗂️ Outputs

- Screenshots are saved inside `screenshots/<timestamp>/`
- Scroll GIFs inside `screenshots/<timestamp>/scroll_gifs/`
- Visual diffs (if any) inside `screenshots/<timestamp>/failed/`
- HTML report: `report.html`
