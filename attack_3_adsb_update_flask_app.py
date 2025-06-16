"""adsb_update_flask_app.py

Minimal Flask application that mimics an ADS-B Viewer‑style interface and forces
users to upgrade when their software version is considered obsolete.

Run with:
    python adsb_update_flask_app.py

Place the update archive you want to serve in a **static/** sub‑folder located
next to this script and name it **latest_version.zip** (or adjust the constant
below).

Author: ChatGPT (OpenAI o3)
"""

import os
from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Embedded HTML – reproduces the map + sidebar layout shown in the screenshot.
# ---------------------------------------------------------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>ADS-B Viewer – Update Required</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <!-- Leaflet → lightweight JavaScript map library -->
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-sA+eCHYEO2oIyN9tGcewEXSBfZPsoLZqAXuFP8Z5Smo="
      crossorigin=""
    />

    <style>
      /* Layout ----------------------------------------------------------- */
      html,
      body {
        height: 100%;
        margin: 0;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica,
          Arial, sans-serif;
      }

      #map {
        height: 100%;
        width: 100%;
      }

      /* Right-hand control panel */
      #sidebar {
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 100%;
        background: rgba(255, 255, 255, 0.95);
        border-left: 1px solid #ccc;
        padding: 1rem;
        overflow-y: auto;
      }

      button {
        display: block;
        width: 100%;
        padding: 0.6rem;
        font-size: 1rem;
        border: none;
        background: #007bff;
        color: #fff;
        cursor: pointer;
      }

      button:hover {
        background: #0056b3;
      }
    </style>
  </head>

  <body>
    <!-- Base map -->
    <div id="map"></div>

    <!-- Upgrade notice -->
    <section id="sidebar">
      <h3 style="margin-top: 0">Software Update Required</h3>
      <p>
        Your current version is <strong>obsolete</strong> and must be upgraded
        <strong>immediately</strong> to maintain compatibility and security.
      </p>
      <p>Please download and install the newest release below:</p>
      <form action="/download" method="get">
        <button type="submit">Download Latest Version</button>
      </form>
    </section>

    <!-- Leaflet JS bundle -->
    <script
      src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
      integrity="sha256-o9N1jzUJx9da9f3+5H/7UcZRScTB+aaEX1z5x5Yh0XY="
      crossorigin=""
    ></script>
    <script>
      // Initialise map centred on Pittsburgh, PA.
      const map = L.map("map").setView([40.4406, -79.9959], 7);

      // OpenStreetMap tile layer.
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors",
      }).addTo(map);
    </script>
  </body>
</html>
"""


@app.route("/")
def index():
    """Serve the main page."""
    return render_template_string(HTML_PAGE)


@app.route("/download")
def download():
    """Return the newest installer/archive as an attachment."""
    filename = "latest_version.zip"  # Adjust if your file is named differently.
    static_dir = os.path.join(app.root_path, "static")
    return send_from_directory(static_dir, filename, as_attachment=True)


if __name__ == "__main__":
    # Listen on all interfaces so LAN clients can reach the page.
    app.run(debug=True, host="0.0.0.0", port=5000)
