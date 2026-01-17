import requests
from pathlib import Path
from html import escape

# Microsoft Learn Catalog API
CATALOG_API = "https://learn.microsoft.com/api/catalog/?type=modules&locale=en-us"

OUTPUT_FILE = "modules.html"


def fetch_modules():
    res = requests.get(CATALOG_API, timeout=15)
    res.raise_for_status()
    return res.json()


def generate_html(modules, limit=20):
    cards_html = ""

    for i, m in enumerate(modules[:limit], start=1):
        title = escape(m.get("title", ""))
        summary = escape(m.get("summary", ""))
        uid = escape(m.get("uid", ""))
        levels = ", ".join(m.get("levels", []))
        roles = ", ".join(m.get("roles", []))
        duration = m.get("duration_in_minutes", "N/A")
        rating = m.get("rating", {}).get("average", "N/A")
        url = m.get("url", "#")

        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <span class="index">#{i}</span>
                <a href="{url}" target="_blank">{title}</a>
            </div>
            <div class="card-body">
                <p class="summary">{summary}</p>
                <ul>
                    <li><b>UID:</b> {uid}</li>
                    <li><b>Level:</b> {levels}</li>
                    <li><b>Roles:</b> {roles}</li>
                    <li><b>Duration:</b> {duration} minutes</li>
                    <li><b>Rating:</b> {rating}</li>
                </ul>
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Microsoft Learn Modules</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            padding: 40px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .container {{
            max-width: 1100px;
            margin: auto;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }}
        .card-header {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .card-header a {{
            text-decoration: none;
            color: #0078d4;
        }}
        .index {{
            color: #666;
            margin-right: 8px;
        }}
        .summary {{
            color: #333;
            margin-bottom: 10px;
        }}
        ul {{
            padding-left: 18px;
        }}
        li {{
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Microsoft Learn – Training Modules</h1>
        {cards_html}
    </div>
</body>
</html>
"""
    return html


def main():
    print("🔄 Fetching modules from Microsoft Learn...")
    data = fetch_modules()
    modules = data.get("modules", [])

    if not modules:
        print("❌ No modules found")
        return

    html = generate_html(modules)

    Path(OUTPUT_FILE).write_text(html, encoding="utf-8")
    print(f"✅ HTML exported: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
