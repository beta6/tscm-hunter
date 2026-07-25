
# 🕵️ TSCM Hunter V2.0

[![GitHub Repository](https://img.shields.io/badge/GitHub-beta6%2Ftscm--hunter-blue?logo=github)](https://github.com/beta6/tscm-hunter)
[![Documentation](https://img.shields.io/badge/TuxRincon-Read_the_Blog_Post-orange)](https://www.tuxrincon.com/es/mblog/tscm-hunter-anti-surveillance/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux%20%7C%20Debian-dragon)](https://www.kali.org/)

**TSCM Hunter** is an open-source Technical Surveillance Counter-Measures suite designed for Kali Linux and Debian-based security distributions. It transforms a standard laptop, a low-cost RTL-SDR receiver, and standard wireless adapters into an integrated RF sweeping and electronic bug detection station.

Whether you are performing routine physical security audits or searching for unverified transmitters, TSCM Hunter helps locate covert RF bugs, hidden IP cameras, rogue Bluetooth trackers, and active cellular bursts.

**📖 Extended Documentation & Technical Details:** Read the full article on technical mechanics, signal analysis, and real-world field use cases at [Tux Rincon: TSCM Hunter Anti-Surveillance](https://www.tuxrincon.com/es/mblog/tscm-hunter-anti-surveillance).

---

## 📋 Table of Contents

- [✨ Main Features](#-main-features)
- [🔬 Architecture & How It Works](#-architecture--how-it-works)
- [⚙️ Requirements & Hardware](#️-requirements-and-hardware)
- [🚀 Installation](#-installation)
- [🛠️ Usage and Switches](#️-usage-and-switches)
  - [Available Parameters](#available-parameters)
  - [Practical Examples](#practical-examples)
- [📊 Log Output and Reporting](#-log-output-and-reporting)
- [❓ Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👨‍💻 Credits and Acknowledgments](#-credits-and-acknowledgments)
- [⚠️ Legal Notice and Disclaimer](#️-legal-notice-and-disclaimer)

---

## ✨ Main Features

* **Radiofrequency Sweep (SDR):** Scans targeted spectrum bands (VHF/UHF) via RTL-SDR to measure anomalous spectral power density and highlight active analog transmissions.
* **Cellular Inspection:** Monitors continuous burst activity across common cellular bands (e.g., GSM 900/1800, subject to SDR hardware frequency limits).
* **Wi-Fi Hunter (Monitor Mode):** Switches compliant Wi-Fi adapters into monitor mode, performs active channel hopping, and captures frame headers to reveal covert IP cameras and wireless micro-recorders (including hidden SSIDs) sorted by RSSI proximity.
* **Bluetooth / BLE Detector:** Interfaces with the system BlueZ stack to discover and log nearby Bluetooth Classic and BLE beacons (AirTags, smart trackers, wireless audio bugs).
* **Acoustic Coupling Check (Larsen Effect):** Demodulates detected RF audio signals on the fly and plays them through the host speaker to excite feedback loops (confirmation beep) when an active audio bug is in physical range.
* **Fine Localization Meter:** Provides a real-time terminal RSSI display with ASCII signal strength bars to facilitate pinpoint triangulation using directional antennas.
* **Configurable Thresholds & Reports:** Enables custom threshold configurations for RF, cellular, Wi-Fi, and Bluetooth scans, with automatic export to structured log files.

---

## 🔬 Architecture & How It Works

TSCM Hunter operates by integrating multiple hardware subsystems into a unified scanning interface:


```

```
              ┌──────────────────────────────────────────┐
              │            TSCM Hunter Engine            │
              └────────────────────┬─────────────────────┘
                                   │
    ┌──────────────────────────────┼──────────────────────────────┐
    │                              │                              │

```

┌───────▼───────┐              ┌───────▼───────┐              ┌───────▼───────┐
│ RTL-SDR Tuner │              │ Wi-Fi Monitor │              │ BlueZ Adapter │
└───────┬───────┘              └───────┬───────┘              └───────┬───────┘
│                              │                              │
RF / Cellular                  Wi-Fi Packets                 BLE & BT Classic
Power Sweeps                    & Proximity                      Beacons

```

1. **RF Processing:** Leverages `rtl_power` / `sox` utilities and Python wrappers to sweep designated spectrum blocks and flag signals exceeding calibrated noise floors.
2. **Wireless Traffic Analysis:** Automates interface mode switching (`iw`, `airmon-ng`) to observe IEEE 802.11 management/data frames and estimate target distance via signal strength.
3. **Bluetooth Scanning:** Queries HCI sockets via `hcitool` / `bluetoothctl` interfaces to capture advertising frames from hidden or unbonded peripherals.

---

## ⚙️ Requirements and Hardware

### Operating System
* **Kali Linux 2026+** (Recommended)
* Debian 12+, Ubuntu 24.04 LTS, or derivative penetration testing distributions.

### Required Software Dependencies
* Python 3.10+
* `rtl-sdr` driver suite
* `sox` audio utility library
* `net-tools`, `wireless-tools`, `iw`
* `bluez` & `bluez-utils`

### Recommended Hardware
* **SDR Hardware:** RTL2832U-based USB dongle (RTL-SDR v3/v4 or NooElec NESDR).
* **Wi-Fi Adapter:** External USB Wi-Fi card supporting **Monitor Mode** and **Packet Injection** (e.g., Alfa AWUS036ACH / AWUS036NHA).
* **Bluetooth Adapter:** Built-in Bluetooth host controller or USB Bluetooth dongle.
* **Audio Output:** Integrated speaker or standard 3.5mm headphones for Larsen feedback verification.
* **Optional:** Directional Log-Periodic or Yagi antenna for fine localization mode.

---

## 🚀 Installation

Clone the [official repository](https://github.com/beta6/tscm-hunter), navigate to the project directory, and execute the automated setup script to configure system packages, udev permissions, and Python environments.

```bash
# Clone the repository
git clone [https://github.com/beta6/tscm-hunter.git](https://github.com/beta6/tscm-hunter.git)

# Enter project directory
cd tscm-hunter

# Grant execution permissions to setup script
chmod +x install.sh

# Run installer with elevated privileges
sudo ./install.sh

```

### Manual Dependency Installation (Alternative)

If you prefer installing dependencies manually without using `install.sh`:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip rtl-sdr sox libsox-fmt-all iw wireless-tools bluez
pip3 install -r requirements.txt

```

## 🛠️ Usage and Switches

> ⚠️ **Privilege Requirement:** TSCM Hunter requires `root` execution privileges to access raw USB devices (RTL-SDR), alter network interface wireless modes, and interact with lower-level Bluetooth HCI sockets.

```bash
sudo python3 tscm_hunter.py [OPTIONS]

```

### Available Parameters

| Switch / Flag | Long Name | Description | Default Value |
| --- | --- | --- | --- |
| `-s` | `--start` | Start frequency for RF sweep (MHz) | `85.0` |
| `-e` | `--end` | End frequency for RF sweep (MHz) | `110.0` |
| `--trf` | `--trf` | Alert threshold trigger for RF sweeps (dB) | `-30.0` |
| `--tcell` | `--tcell` | Alert threshold trigger for cellular bands (dB) | `-30.0` |
| `--twifi` | `--twifi` | RSSI alert threshold for Wi-Fi targets (dBm) | `-65.0` |
| `--tbt` | `--tbt` | RSSI alert threshold for Bluetooth devices (dBm) | `-65.0` |
| `-d` | `--duration` | Duration window for Wi-Fi and BT scan loops (seconds) | `10` |
| `-l` | `--locate` | Direct fine-localization mode targeting a specific frequency (MHz) | Disabled |
| `-o` | `--output` | Destination file path for generated execution report | `tscm_report_DATETIME.log` |
| `-a` | `--all` | Paranoid mode (disables thresholds to output all detected signals) | `False` |
| `-h` | `--help` | Display CLI help menu and parameter reference | — |

---

### Practical Examples

#### 1. Standard Sweep

Executes a baseline sweep using default settings (VHF band 85–110 MHz, standard RSSI filters for Wi-Fi and Bluetooth):

```bash
sudo python3 tscm_hunter.py

```

#### 2. Custom Proximity Threshold Tuning

Tighten alert thresholds to isolate close-proximity signals and eliminate ambient noise from adjacent rooms or external networks:

```bash
sudo python3 tscm_hunter.py --trf -20 --tcell -25 --twifi -45 --tbt -50

```

#### 3. UHF Band Sweep & Report Generation

Scan the UHF range (400–450 MHz) commonly used by handheld radio transmitters and save findings to a custom log file:

```bash
sudo python3 tscm_hunter.py -s 400.0 -e 450.0 -o boardroom_uhf_report.log

```

#### 4. "Paranoid" Unfiltered Scan

Capture and record all detectable spectrum signals regardless of signal strength:

```bash
sudo python3 tscm_hunter.py -a -o full_unfiltered_report.log

```

#### 5. Direct Fine Localization

Target a known frequency (e.g., 433.92 MHz) with a directional antenna to trace transmitter location in real time:

```bash
sudo python3 tscm_hunter.py -l 433.92

```

---

## 📊 Log Output and Reporting

When TSCM Hunter completes a session, detailed diagnostic information is stored in the designated log file (`tscm_report_DATETIME.log`).

### Example Log Structure

```text
================================================================================
                        TSCM HUNTER AUDIT REPORT
================================================================================
Timestamp: 2026-07-25 14:30:12 UTC
Target Sweep Range: 85.0 MHz - 110.0 MHz
Configured Thresholds: RF: -30.0dB | Wi-Fi: -65.0dBm | BT: -65.0dBm
--------------------------------------------------------------------------------

[!] RF SWEEP ALERTS DETECTED:
  - Freq: 102.400 MHz | Power: -18.4 dB | Status: EXCEEDS_THRESHOLD

[!] WI-FI TARGETS IN PROXIMITY:
  - BSSID: AA:BB:CC:DD:EE:FF | SSID: [HIDDEN] | RSSI: -42 dBm | Ch: 6

[!] BLUETOOTH / BLE DEVICES DETECTED:
  - MAC: 11:22:33:44:55:66 | Name: Unknown BLE Beacon | RSSI: -58 dBm

--------------------------------------------------------------------------------
Audit completed. Report saved to: boardroom_uhf_report.log
================================================================================

```

---

## ❓ Troubleshooting

* **Issue: `Kernel driver detached` or `USB device busy` error when accessing RTL-SDR.**
* *Solution:* Blacklist the default DVB-T driver or unload it manually:
```bash
sudo rmmod dvb_usb_rtl28xxu

```




* **Issue: Wi-Fi card fails to switch to monitor mode.**
* *Solution:* Kill conflicting processes before starting the scan:
```bash
sudo airmon-ng check kill

```




* **Issue: No Bluetooth devices detected.**
* *Solution:* Ensure the BlueZ daemon is active and interface is powered up:
```bash
sudo systemctl restart bluetooth
sudo hciconfig hci0 up

```





---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the project repository on [GitHub](https://github.com/beta6/tscm-hunter).
2. Create your feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add new TSCM module'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request detailing your enhancements.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for full licensing details.

---

## 👨‍💻 Credits and Acknowledgments

This project was designed, developed, and tested under the conceptual and technical supervision of **[beta6](https://github.com/beta6)**.

For further guides, technical writeups, and security research related to Linux, penetration testing, and counter-surveillance techniques, visit the official blog:
👉 **[Tux Rincon Blog](https://www.tuxrincon.com/es/mblog/tscm-hunter-anti-surveillance)**

---

## ⚠️ Legal Notice and Disclaimer

**This software is provided STRICTLY for educational, research, and authorized security auditing purposes.**

* **Technical Limitations & Hardware Realism:** Low-cost RTL-SDR receivers provide accessible entry-level spectrum analysis, but **do not** replace professional laboratory spectrum analyzers, non-linear junction detectors (NLJD), or certified TSCM hardware. False positives may occur due to local noise floors, ambient harmonics, or front-end tuner saturation. Do not rely exclusively on this tool to certify high-security environments.
* **Authorized Use and Legal Compliance:** Radio frequency monitoring and wireless packet capture are governed by local and international telecommunications regulations. Run this tool strictly on systems, networks, and physical locations where you have explicit, written authorization from the property owner or governing authority.
* **Disclaimer of Liability:** Neither the author (**beta6**) nor **Tux Rincon** assume any liability for damage, financial loss, regulatory violations, or legal actions resulting from misuse of this software.

```

```
