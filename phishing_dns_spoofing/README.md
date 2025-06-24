# Security Course: Attack Demonstrations

This repository contains demonstration scripts and servers for various network and application security attacks, including DNS spoofing, ARP spoofing, and command injection. The examples are intended for educational and controlled lab environments only.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [DNS Spoofing Demo](#dns-spoofing-demo)
- [Command Injection Demo](#command-injection-demo)
- [Notes](#notes)

---

## Prerequisites
- Python 3.x
- Flask (`pip install flask`)
- Linux utilities: `bettercap`, `iptables`, `ping` (for ARP/DNS spoofing scripts)
- Windows/Linux for running payloads and servers
- Run all scripts with appropriate privileges (some require `sudo`)

## Project Structure
- `phishing_dns_spoofing/`
  - `dns_spoofing.py` — Flask web server for fake update page
  - `dns_spoofing.sh` — Bash script to perform ARP and DNS spoofing
  - `static/ADS-B-Display-latest.exe` — Fake update executable
  - `static/adsbhub.png` — Background image for phishing page
- `command_injection/`
  - `server.py` — Reverse shell and payload delivery server
  - `ADSB-hub_dump/` — Windows payload source and binaries

## DNS Spoofing Demo
This attack demonstrates phishing via DNS spoofing and a fake update page.

### 0. Update Listener IP Address and Network Configuration

Before running the attack, set the correct IP address for the reverse shell listener and update your network configuration:

- Edit the following line in `ADS-B-Display_patch/patches/SimpleCSVtoBigQuery_hacked.py`:

```python
LISTENER_IP = "<your_attacker_machine_ip>"
```
Replace `<your_attacker_machine_ip>` with the IP address of your attacker/listener machine. This ensures the reverse shell connects to the correct host.

- Edit `config.sh` to set the correct IP addresses and network interface for your environment:
  - `PI_ADDRESS`, `DISPLAY_ADDRESS`, `HACK_HOST_MACHINE`, `HACK_LINUX_MACHINE`, and `INTERFACE`

This ensures all scripts use the correct network settings for your lab setup.

### 1. Start the Fake Update Web Server
```bash
cd phishing_dns_spoofing
python dns_spoofing.py
```
- The server runs on `http://0.0.0.0:5000`.
- The update page is served at `/` and the fake update executable at `/download`.

### 2. Run the DNS/ARP Spoofing Script (on attacker machine)
```bash
sudo ./dns_spoofing.sh
```
- Edits may be needed in `config.sh` for your network (set `INTERFACE`, `DISPLAY_ADDRESS`, `HACK_LINUX_MACHINE`).
- Requires `bettercap` installed.

### 3. On Victim Machine
- When the victim visits the targeted domain (e.g., `data.adsbhub.org`), they are redirected to the attacker's fake update page.
- The victim will download and install the patch.

## Command Injection Demo
This attack demonstrates remote command execution and payload delivery.

### 1. Start the Reverse Shell & HTTP Server
```bash
cd command_injection
python server.py
```
- Listens for reverse shell connections on port 4444.
- Serves the payload (`ADSB-hub_dump.exe`) via HTTP on port 8000.

### 2. On Victim Machine
- After user "unchecked" the BigQuerry checkbox, then
  - The attacker sends a command to download and execute the payload using PowerShell.
  - The victim's shell is accessible via the attacker's terminal.

## ARP Spoofing & Tampering
See `tampering_arp_spoofing/` for additional scripts and instructions for ARP spoofing and data manipulation.
