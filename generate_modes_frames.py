#!/usr/bin/env python3
"""generate_modes_frames.py

Standalone script (no external ADS‑B encode library needed) that converts a CSV
flight path into Mode S DF 17 frames:
    • Type‑Code 1   – Aircraft identification (callsign)
    • Type‑Code 11  – Airborne position (even / odd CPR)
    • Type‑Code 19  – Ground speed / track / vertical rate

Outputs two files:
    <prefix>.hex  –  one 112‑bit frame per line (28 hex chars)
    <prefix>.bin  –  raw binary   (14 bytes per frame)

CSV **must** contain columns:
    timestamp (ISO8601), lat, lon, alt_ft, gs_knots, track_deg, vert_rate_fpm

Usage example:
    python generate_modes_frames.py \
        --csv aim_high_dataset.csv \
        --icao A0B1C2 \
        --callsign AIMHIGH \
        --output aim_high_modes

No 3rd‑party encoder needed – all math (CRC‑24, CPR, altitude, velocity) is
implemented below (~120 LOC).
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import pandas as pd

###############################################################################
# ▼▼▼   Basic bit helpers & CRC‑24 implementation   ▼▼▼
###############################################################################

_G_POLY = 0xFFF409  # Mode S generator polynomial (x^24 + x^23 + ... + 1)


def _crc24(bits: str) -> int:
    """Return CRC‑24 parity for *bits* (string of 88 or 112 bits)."""
    crc = 0
    for bit in bits:
        top = (crc >> 23) & 1
        crc = ((crc << 1) & 0xFFFFFF) | int(bit)
        if top ^ int(bit):
            crc ^= _G_POLY
    return crc


def _bin(n: int, length: int) -> str:
    """Binary string, zero‑padded to *length*."""
    return format(n & ((1 << length) - 1), f"0{length}b")


def _hex(bits: str) -> str:
    return f"{int(bits, 2):028X}"

###############################################################################
# ▼▼▼   Callsign  (Type‑Code 1)   ▼▼▼
###############################################################################

_CHARSET = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### #####0123456789#####"


def encode_callsign(icao: str, callsign: str) -> str:
    """Return DF17 TC1 frame (28 hex chars)."""
    cs = callsign.upper().ljust(8)[:8]
    body = (
        _bin(17, 5)                    # DF=17
        + _bin(5, 3)                   # CA=5 (level 2 transponder)
        + _bin(int(icao, 16), 24)
        + _bin(1, 5)                   # TC=1 (ident)
        + _bin(0, 3)                   # Emitter category
        + "".join(_bin(_CHARSET.find(ch) % 32, 6) for ch in cs)
    )
    parity = _bin(_crc24(body), 24)
    return _hex(body + parity)

###############################################################################
# ▼▼▼   CPR helpers for Airborne Position (TC 11)   ▼▼▼
###############################################################################

# NL function table from Annex 10 (lat zoning)
_NL_TABLE = [
    59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41,
    40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22,
    21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
]


def _cprNL(lat: float) -> int:
    lat = abs(lat)
    if lat < 10.47047130:
        return 59
    for i, a in enumerate(
        [10.47047130, 14.82817437, 18.18626357, 21.02939493, 23.54504487,
         25.82924707, 27.93898710, 29.91135686, 31.77209708, 33.53993436,
         35.22899598, 36.85025108, 38.41241892, 39.92256684, 41.38651832,
         42.80914012, 44.19454951, 45.54626723, 46.86733252, 48.16039128,
         49.42776439, 50.67150166, 51.89342469, 53.09516153, 54.27817472,
         55.44378444, 56.59318756, 57.72747354, 58.84763776, 59.95459277,
         61.04917774, 62.13216659, 63.20427479, 64.26616523, 65.31845310,
         66.36171008, 67.39646774, 68.42322022, 69.44242631, 70.45451075,
         71.45986473, 72.45884545, 73.45177442, 74.43893416, 75.42056257,
         76.39684391, 77.36789461, 78.33374083, 79.29428225, 80.24923213,
         81.19801349, 82.13956981, 83.07199445, 83.99173563, 84.89166191,
         85.75541621, 86.53536998, 87.00000000]
    ):
        if lat < a:
            return 59 - i
    return 1


def _cpr_encode(lat: float, lon: float, odd: int) -> tuple[int, int]:
    dlat = 360.0 / (60 if odd == 0 else 59)
    lat_i = math.floor((lat + 90) / dlat)
    lat_cpr = int(((lat + 90) % dlat) / dlat * 131072 + 0.5)

    nl = _cprNL(lat) - (odd == 1)
    dlon = 360.0 / nl if nl else 360.0
    lon_i = math.floor((lon + 180) / dlon)
    lon_cpr = int(((lon + 180) % dlon) / dlon * 131072 + 0.5)
    return lat_cpr & 0x1FFFF, lon_cpr & 0x1FFFF  # 17 bits each


def encode_position(icao: str,
                    lat: float, lon: float,
                    alt_ft: int,
                    ts_unused: int,
                    odd: int) -> str:
    # 1️⃣  Độ cao (11 bit, Q-bit nằm bên trong **không thêm bít mới**)
    alt_code = int((alt_ft + 1000) / 25) | (1 << 4)   # bảo đảm Q = 1
    alt_bits = _bin(alt_code, 11)                     # ⬅️ 11 bit, KHÔNG 12

    # 2️⃣  CPR
    lat_cpr, lon_cpr = _cpr_encode(lat, lon, odd)

    # 3️⃣  Ghép ME = 56 bit
    body = (
        _bin(17, 5)               # DF17
        + _bin(5, 3)              # CA
        + _bin(int(icao, 16), 24)
        + _bin(11, 5)             # TC 11
        + _bin(0, 3)              # SS
        + _bin(0, 1)              # NIC-sb
        + _bin(odd, 1)            # **T flag = odd**
        + _bin(odd, 1)            # F = odd
        + alt_bits                # 11 bit ALT (đã có Q)
        + _bin(lat_cpr, 17)
        + _bin(lon_cpr, 17)
    )
    parity = _bin(_crc24(body), 24)
    return _hex(body + parity)    # → luôn 28 ký tự

###############################################################################
# ▼▼▼   Velocity (Type‑Code 19, sub‑type 1 – ground speed)   ▼▼▼
###############################################################################


def encode_velocity(icao: str, gs_kn: int, track: int, v_rate_fpm: int) -> str:
    """DF17 TC19 Subtype 1 – ground speed / track / vertical‑rate (56‑bit ME).

    The ME field layout we implement (Annex 10 Table B‑2‑84):
        •  1‑5  TC   (19)
        •  6‑8  Sub‑type (1)
        •  9    Intent Change (0)
        • 10    IF‑RC (0)
        • 11‑20 Ground speed  (10 b, LSB = 1 kt, 0=invalid)
        • 21‑30 Track angle   (10 b, LSB = 360/1024 deg)
        • 31    Reserved = 0
        • 32    Vr sign (0=up,1=down)
        • 33‑41 Vertical rate (9 b, LSB = 64 ft/min, 0=invalid)
        • 42‑56 Reserved = 0 (fill‑bits)
    """
    # --- fields -------------------------------------------------------------
    sub = 1
    ic  = 0  # Intent change
    ifrc = 0 # IF‑RC capability

    gs   = max(0, min(int(gs_kn), 1023))            # 10 bits
    gs_bits = _bin(gs, 10)

    trk = int(round(track % 360 * 1024 / 360))       # 10 bits
    trk_bits = _bin(trk, 10)

    vr_sign = 0 if v_rate_fpm >= 0 else 1
    vr_val  = min(abs(int(v_rate_fpm)) // 64, 511)   # 9 bits
    vr_bits = _bin(vr_val, 9)

    me = (
        _bin(19, 5)
        + _bin(sub, 3)
        + _bin(ic, 1)
        + _bin(ifrc, 1)
        + gs_bits
        + trk_bits
        + _bin(0, 1)        # reserved bit 31
        + _bin(vr_sign, 1)
        + vr_bits
        + _bin(0, 56)[:56]  # ensure total ME = 56 (extra padding trimmed)
    )
    me = me[:56]  # trim to exactly 56 bits

    header = _bin(17, 5) + _bin(5, 3) + _bin(int(icao, 16), 24)
    body = header + me
    parity = _bin(_crc24(body), 24)
    return _hex(body + parity)

###############################################################################
# ▼▼▼   CLI & file output   ▼▼▼
###############################################################################

def build_frames(df: pd.DataFrame, icao: str, callsign: str) -> list[str]:
    frames: list[str] = []
    last_cs_ts = 0
    for r in df.itertuples(index=False):
        ts = int(r.timestamp.timestamp())
        if ts - last_cs_ts >= 5:
            frames.append(encode_callsign(icao, callsign))
            last_cs_ts = ts
        frames.append(encode_position(icao, r.lat, r.lon, int(r.alt_ft), ts, 0))
        frames.append(encode_position(icao, r.lat, r.lon, int(r.alt_ft), ts + 1, 1))
        frames.append(encode_velocity(icao, int(r.gs_knots), int(r.track_deg), int(r.vert_rate_fpm)))
    return frames


def main() -> None:  # pragma: no cover
    p = argparse.ArgumentParser(description="CSV → Mode S DF17 frame generator")
    p.add_argument("--csv", required=True)
    p.add_argument("--icao", required=True, help="24‑bit hex, e.g. A0B1C2")
    p.add_argument("--callsign", required=True, help="Aircraft callsign, ≤8 chars")
    p.add_argument("--output", default="modes_out", help="Output prefix")
    args = p.parse_args()

    df = pd.read_csv(args.csv, parse_dates=["timestamp"])
    req = {"timestamp", "lat", "lon", "alt_ft", "gs_knots", "track_deg", "vert_rate_fpm"}
    if not req.issubset(df.columns):
        sys.exit("CSV thiếu cột: " + ", ".join(sorted(req - set(df.columns))))

    frames = build_frames(df, args.icao.upper(), args.callsign[:8].ljust(8))
    print(f"Generated {len(frames)} frames")

    hex_path = Path(f"{args.output}.hex")
    bin_path = Path(f"{args.output}.bin")
    hex_path.write_text("\n".join(frames))
    with bin_path.open("wb") as fb:
        for f in frames:
            fb.write(bytes.fromhex(f))
    print("Saved:", hex_path, "&", bin_path)


if __name__ == "__main__":
    main()

# python3 generate_modes_frames.py \
#   --csv aim_high_dataset.csv \
#   --icao 4d2023 \
#   --callsign AIMHIGH \
#   --output aim_high_modes