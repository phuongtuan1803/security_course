#!/usr/bin/env python3
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import math
import sys

# 1. Read image + convert to black-and-white binary
if len(sys.argv) < 2:
    print("Usage: python3 pixel_to_gps.py <image_path>")
    sys.exit(1)
image_path = sys.argv[1]
img = Image.open(image_path).convert("RGB")
gray = ImageOps.grayscale(img)

threshold = 50                        # background separation threshold
binary = gray.point(lambda x: 255 if x > threshold else 0, mode="1")
binary = binary.resize((100, 100))    # 100×100 pixels

# 2. Convert to NumPy bool (True = white pixel)
arr = np.array(binary, dtype=bool)    # shape (h, w)
h, w = arr.shape

# 3. Function to convert pixel → GPS coordinates
lat0, lon0 = 40.4406, -79.9959
def pixel_to_gps(px, py, *, meters_per_pixel=1000):
    dx = (px - w / 2) * meters_per_pixel          # +east
    dy = (py - h / 2) * meters_per_pixel          # +south
    lat = lat0 - dy / 111_320                     # +north
    lon = lon0 + dx / (111_320 * math.cos(math.radians(lat0)))
    return lat, lon

# 4. Vectorize: get all True pixels
ys, xs = np.where(arr)            # coordinates (row, column) of white pixels
lats, lons = zip(*(pixel_to_gps(x, y) for x, y in zip(xs, ys)))

df = pd.DataFrame({
    # icao,callsign,lat,lon,alt,gs,trk,vr
    "icao": [f"A{str(i+1).zfill(5)}" for i in range(len(lats))],
    "callsign": ["AIMHIGH"] * len(lats),
    "lat": lats,
    "lon": lons,
    "alt": [36000] * len(lats),
    "gs": [0] * len(lats),
    "trk": [158] * len(lats),
    "vr": [-1800] * len(lats)
    # "pixel_x": xs,
    # "pixel_y": ys
})

csv_path = "aim_high_dataset.csv"
df.to_csv(csv_path, index=False)
print(f"Saved {len(df)} points → {csv_path}")
