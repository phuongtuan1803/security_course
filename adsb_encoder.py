#!/usr/bin/env python3
"""adsb_encoder.py – revised with sender

*Bug‑fix*: `encode_velocity()` now pads the ME field to **exactly 56 bits**.
*Extension*: CSV loader + file writer + network sender with message rate (messages per second).
"""

import argparse, csv, math, time, socket
from typing import List

# ─── Constants ──────────────────────────────────────────────────────────────
_CHARSET = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"
DF, CA, CRC_POLY = 17, 5, 0xFFF409
NZ = 15
D_LAT_EVEN = 360.0 / (4 * NZ)
D_LAT_ODD  = 360.0 / (4 * NZ - 1)
_2POW17 = 1 << 17

# ─── Bit helpers ────────────────────────────────────────────────────────────
def _bits_to_hex(bits: str) -> str:
    return int(bits, 2).to_bytes(14, "big").hex().upper()

def _crc24(msg_bits: str) -> int:
    data = [int(b) for b in msg_bits] + [0]*24
    for i in range(len(msg_bits)):
        if data[i]:
            for p in range(24):
                if (CRC_POLY >> (23-p)) & 1:
                    data[i+p+1] ^= 1
    rem = 0
    for b in data[-24:]:
        rem = (rem<<1)|b
    return rem

def _assemble(df:int, ca:int, icao:int, me_bits:str) -> str:
    aft88 = f"{df:05b}{ca:03b}{icao:024b}{me_bits}"
    if len(me_bits)!=56:
        raise ValueError(f"ME field must be 56 bits, got {len(me_bits)}")
    return "*"+_bits_to_hex(aft88+f"{_crc24(aft88):024b}")+";"

# ─── Encoders ───────────────────────────────────────────────────────────────
def encode_callsign(icao_hex:str, callsign:str)->str:
    print(f"Encoding callsign: icao={icao_hex}, callsign={callsign}")
    icao=int(icao_hex,16)
    cs=callsign.strip().upper().ljust(8)
    six="".join(f"{_CHARSET.index(c):06b}" if c in _CHARSET else"000000" for c in cs)
    me=f"{1:05b}"+"000"+six
    return _assemble(DF,CA,icao,me)

def _cpr_NL(lat:float)->int:
    lat=abs(lat)
    thresholds=[10.47047130,14.82817437,18.18626357,21.02939493,23.54504487,25.82924707,27.93898710,29.91135686,31.77209708,33.53993436,35.22899598,36.85025108,38.41241892,39.92256684,41.38651832,42.80914012,44.19454951,45.54626723,46.86733252,48.16039128,49.42776439,50.67150166,51.89342469,53.09516153,54.27817472,55.44378444,56.59318756,57.72747354,58.84763776,59.95459277,61.04917774,62.13216659,63.20427479,64.26616523,65.31845310,66.36171008,67.39646774,68.42322022,69.44242631,70.45451075,71.45986473,72.45884545,73.45177442,74.43893416,75.42056257,76.39684391,77.36789461,78.33374083,79.29428225,80.24923213,81.19801349,82.13956981,83.07199445,83.99173563,84.89166191,85.75541621,86.53536998,87]
    nl_table=list(range(59,1,-1))
    for t,nl in zip(thresholds,nl_table):
        if lat<t:
            return nl
    return 1

def encode_position(icao_hex:str,lat:float,lon:float,alt_ft:int,even:bool)->str:
    icao=int(icao_hex,16)
    q=1
    n_alt=int((alt_ft+1000)/25)
    alt=f"{n_alt:011b}"
    alt_bits=alt[:4]+str(q)+alt[4:]

    d_lat=D_LAT_EVEN if even else D_LAT_ODD
    fflag=0 if even else 1

    lat_idx=math.floor(lat/d_lat)
    lat_cpr=int(round(((lat/d_lat)-lat_idx)*_2POW17))&0x1FFFF

    nl=_cpr_NL(lat)-(0 if even else 1)
    d_lon=360.0/max(nl,1)
    lon_idx=math.floor(lon/d_lon)
    lon_cpr=int(round(((lon/d_lon)-lon_idx)*_2POW17))&0x1FFFF

    # Fields per DO-260B: TC | SS=0,NIC_A=0 | altitude | time flag=0 | fflag | lat | lon
    me=(
        f"{11:05b}"   # type code 11 (airborne position, baro alt)
        + "000"       # Surveillance status (00) + NIC Supplement-A (0)
        + alt_bits    # 12-bit altitude with Q=1
        + "0"         # Time flag: always 0 (no UTC sync)
        + str(fflag)  # Odd(1)/Even(0) frame indicator
        + f"{lat_cpr:017b}{lon_cpr:017b}"
    )
    return _assemble(DF,CA,icao,me)

def encode_velocity(icao_hex:str,gs_kn:float,track_deg:float,vr_fpm:int)->str:
    print(f"Encoding velocity: icao={icao_hex}, gs_kn={gs_kn}, track_deg={track_deg}, vr_fpm={vr_fpm}")
    icao=int(icao_hex,16)
    v_e=gs_kn*math.sin(math.radians(track_deg));v_n=gs_kn*math.cos(math.radians(track_deg))
    ew_dir=0 if v_e>=0 else 1;ns_dir=0 if v_n>=0 else 1
    ew_vel=min(int(abs(v_e)+0.5),1023);ns_vel=min(int(abs(v_n)+0.5),1023)
    print(f"  ew_dir={ew_dir}, ew_vel={ew_vel}, ns_dir={ns_dir}, ns_vel={ns_vel}")
    vr_sign=0 if vr_fpm>=0 else 1;vr_rate=min(int(abs(vr_fpm)/64+0.5),511)
    me=(f"{19:05b}"+"001"+"0"+"0"+"00"+
        str(ew_dir)+f"{ew_vel:010b}"+str(ns_dir)+f"{ns_vel:010b}"+
        "0"+str(vr_sign)+f"{vr_rate:09b}"+"000000")
    me=me.ljust(56,'0')
    
    return _assemble(DF,CA,icao,me)

# ─── Sender ─────────────────────────────────────────────────────────────────
def send_csv_lines_to_port(csv_path:str, rate_mps:float, host:str="127.0.0.1", port:int=30001):
    with open(csv_path, newline='') as f:
        rdr = csv.DictReader(f)
        even_flag = True
        delay = 1.0 / rate_mps if rate_mps > 0 else 1.0
        for row in rdr:
            icao = row['icao']
            cs = row.get('callsign', 'UNKNOWN')
            lat = float(row['lat'])
            lon = float(row['lon'])
            alt = int(row.get('alt', 35000))
            gs  = float(row.get('gs', 450))
            trk = float(row.get('trk', 0))
            vr  = int(row.get('vr', 0))
            frames = [
                encode_callsign(icao, cs),
                encode_velocity(icao, gs, trk, vr),
                encode_position(icao, lat, lon, alt, even=True),
                encode_position(icao, lat, lon, alt, even=False)
            ]
            print("Sending frames for icao:", icao)
            with socket.create_connection((host, port)) as s:
                for f in frames:
                    print("Sending frame:", f)
                    s.sendall((f + "\n").encode())
                    time.sleep(delay)
                    
def load_csv_to_datafile(csv_path:str, out_path:str):
    """Load rows from *csv_path* and write ADS-B frames to *out_path*."""
    with open(csv_path, newline='') as f, open(out_path, 'w') as out:
        rdr = csv.DictReader(f)
        for row in rdr:
            icao = row['icao']
            cs = row.get('callsign', 'UNKNOWN')
            lat = float(row['lat'])
            lon = float(row['lon'])
            alt = int(row.get('alt', 35000))
            gs  = float(row.get('gs', 450))
            trk = float(row.get('trk', 0))
            vr  = int(row.get('vr', 0))

            frames = [
                encode_callsign(icao, cs),
                encode_velocity(icao, gs, trk, vr),
                encode_position(icao, lat, lon, alt, even=True),
                encode_position(icao, lat, lon, alt, even=False),
            ]

            for f in frames:
                out.write(f + "\n")
                
# ─── CLI ─────────────────────────────────────────────────────────────────────
def main():
    p=argparse.ArgumentParser(description="Encode and send ADS-B DF17 frames")
    p.add_argument("--icao");p.add_argument("--callsign")
    p.add_argument("--lat",type=float);p.add_argument("--lon",type=float)
    p.add_argument("--alt",type=int);p.add_argument("--gs",type=float)
    p.add_argument("--trk",type=float);p.add_argument("--vr",type=int,default=0)
    p.add_argument("--csv");p.add_argument("--out")
    p.add_argument("--send", action="store_true")
    p.add_argument("--rate", type=float, default=1.0, help="Message rate in messages per second")
    args=p.parse_args()

    if args.send and args.csv:
        send_csv_lines_to_port(args.csv, args.rate)
    elif args.csv:
        load_csv_to_datafile(args.csv, args.out or "out.data")
    else:
        if not all([args.icao,args.callsign,args.lat,args.lon,args.alt,args.gs,args.trk]):
            p.error("Missing parameters")
        frames=[
            encode_callsign(args.icao,args.callsign),
            encode_velocity(args.icao,args.gs,args.trk,args.vr),
            encode_position(args.icao,args.lat,args.lon,args.alt,True),
            encode_position(args.icao,args.lat,args.lon,args.alt,False)
        ]
        for f in frames:print(f)

if __name__=="__main__":
    main()
