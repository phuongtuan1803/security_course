# How to Run Security Course Scripts

This guide explains how to run the following scripts:
- `tampering_arp_spoofing.sh`
- `tampering_arp_spoofing.py`
- `adsb_encoder.py`
- `config.sh`
- `aim_high_dataset.csv`

## Prerequisites
- Ensure you have `bash`, `python3`, and required Python packages installed.
- You may need `arpspoof` and other network tools.
- Make sure `config.sh` is configured with the correct IP addresses and interface.

## 0. Install `dump1090`
Make the script executable and run it:
```bash
cd
sudo apt update
sudo apt install -y librtlsdr-dev pkg-config build-essential libusb-1.0-0-dev
git clone git@github.com:antirez/dump1090.git
cd dump1090
make
```

## 1. Configure `config.sh`
Edit `config.sh` to set the correct IP addresses and network interface.

## 2. Run `tampering_arp_spoofing.sh`
Make the script executable and run it:
```bash
chmod +x tampering_arp_spoofing.sh
sudo ./tampering_arp_spoofing.sh
```

## 3. Run `adsb_encoder.py`
This script may require additional Python packages. Run:
```bash
python3 adsb_encoder.py --send --csv dataset/aim_high_dataset.csv --rate 1000
```

## 4. Run `tampering_arp_spoofing.py` (TBD)
Make sure Python 3 is installed. Run the script:
```bash
python3 tampering_arp_spoofing.py
```

## Notes
- Always run these scripts with appropriate permissions (use `sudo` if required).
- Ensure you are on the correct network interface as set in `config.sh`.
- For troubleshooting, check script outputs and logs.

### Prepare dataset
Make sure Python 3 is installed. Run the script:
```bash
cd dataset
python3 pixel_to_gps.py aim_high.png
```