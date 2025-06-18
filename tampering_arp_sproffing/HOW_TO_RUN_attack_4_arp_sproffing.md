# How to Run Security Course Scripts

This guide explains how to run the following scripts:
- `attack_4_arp_sproffing.sh`
- `attack_4_arp_sproffing.py`
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
Edit `config.sh` to set the correct IP addresses and network interface. Example:

## 2. Run `attack_4_arp_sproffing.sh`
Make the script executable and run it:
```bash
sudo sh attack_4_arp_sproffing.sh 
```

## 3. Run `adsb_encoder.py`
This script may require additional Python packages. Run:
```bash
python adsb_encoder.py --send --csv aim_high_dataset.csv --rate 2000
```

## 4. Run `attack_4_arp_sproffing.py` (TBD)
Make sure Python 3 is installed. Run the script:
```bash
python3 attack_4_arp_sproffing.py
```

## Notes
- Always run these scripts with appropriate permissions (use `sudo` if required).
- Ensure you are on the correct network interface as set in `config.sh`.
- For troubleshooting, check script outputs and logs.
