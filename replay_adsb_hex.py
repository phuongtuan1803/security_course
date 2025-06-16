#!/usr/bin/env python3
"""
replay_adsb_hex.py
------------------
Replay ADS‑B DF17 hex frames to a dump1090 (or any AVR‑raw listener)
over TCP port 30002.  Each line of the input file must be a 28‑hex‑
character Mode S frame (112 bits).  The script converts each line to 
AVR format (`*HEX;\\r\\n`) and streams them at the user‑selected rate.

Usage
-----
python replay_adsb_hex.py --hex aim_high_modes.hex \
                          --host 127.0.0.1 --port 30002 \
                          --rate 5
"""
import argparse
import logging
import socket
import time
from pathlib import Path

def load_frames(hex_path: Path):
    """Return list of AVR‑formatted frames '*......;'."""
    lines = [ln.strip().upper() for ln in hex_path.read_text().splitlines() if ln.strip()]
    frames = []
    for ln in lines:
        if len(ln) != 28 or any(c not in "0123456789ABCDEF" for c in ln):
            logging.warning("Skipping invalid line: %s", ln)
            continue
        frames.append(f"*{ln};")
    if not frames:
        raise ValueError("No valid 28‑hex frames found!")
    return frames

def main():
    ap = argparse.ArgumentParser(description="Replay ADS‑B hex frames to dump1090 TCP port 30002")
    ap.add_argument("--hex", required=True, help="Path to .hex file (28 hex/line)")
    ap.add_argument("--host", default="127.0.0.1", help="dump1090 host (default: 127.0.0.1)")
    ap.add_argument("--port", type=int, default=30002, help="dump1090 port (default: 30002)")
    ap.add_argument("--rate", type=float, default=5.0, help="frames per second (default: 5)")
    args = ap.parse_args()

    delay = 1.0 / args.rate if args.rate > 0 else 0
    logging.basicConfig(format="%(asctime)s  %(levelname)s: %(message)s", level=logging.INFO)

    frames = load_frames(Path(args.hex))
    logging.info("Loaded %d frames from %s", len(frames), args.hex)

    with socket.create_connection((args.host, args.port)) as sock:
        logging.info("Connected to %s:%d. Streaming at %.2f FPS (Ctrl‑C to stop)…",
                     args.host, args.port, args.rate)
        try:
            while True:
                for idx, fr in enumerate(frames, 1):
                    sock.sendall((fr + "\r\n").encode())
                    logging.info("Sent %s [%d/%d]", fr, idx, len(frames))
                    if delay:
                        time.sleep(delay)
        except KeyboardInterrupt:
            logging.info("Stopped by user (^C)")

if __name__ == "__main__":
    main()
# python replay_adsb_hex.py \
#   --hex aim_high_dataset.data \
#   --host 127.0.0.1 \
#   --port 30001 \
#   --rate 5   