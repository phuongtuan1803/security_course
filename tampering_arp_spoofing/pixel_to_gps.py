#!/usr/bin/env python3
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import math

# 1. Đọc ảnh + chuyển đen-trắng nhị phân
image_path = "arm_high.png"             # đổi tên file nếu cần
img = Image.open(image_path).convert("RGB")
gray = ImageOps.grayscale(img)

threshold = 50                        # ngưỡng tách nền
binary = gray.point(lambda x: 255 if x > threshold else 0, mode="1")
binary = binary.resize((100, 100))    # 100×100 pixel

# 2. Chuyển sang NumPy bool (True = điểm trắng)
arr = np.array(binary, dtype=bool)    # shape (h, w)
h, w = arr.shape

# 3. Hàm chuyển pixel → toạ độ GPS
lat0, lon0 = 40.4406, -79.9959
def pixel_to_gps(px, py, *, meters_per_pixel=1000):
    dx = (px - w / 2) * meters_per_pixel          # +east
    dy = (py - h / 2) * meters_per_pixel          # +south
    lat = lat0 - dy / 111_320                     # +north
    lon = lon0 + dx / (111_320 * math.cos(math.radians(lat0)))
    return lat, lon

# 4. Vector hoá: lấy mọi pixel True
ys, xs = np.where(arr)            # toạ độ (hàng, cột) pixel trắng
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

csv_path = "aim_high_coords.csv"
df.to_csv(csv_path, index=False)
print(f"Saved {len(df)} points → {csv_path}")
