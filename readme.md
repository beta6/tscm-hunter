
# 🕵️‍♂️ TSCM Hunter V2.0

TSCM Hunter is an open-source Technical Surveillance Counter-Measures suite designed for Kali Linux. It transforms your laptop, a low-cost RTL-SDR receiver, and your network adapters into a unified station to sweep and detect covert espionage devices (radio microphones, hidden IP cameras, Bluetooth trackers, and cellular transmitters).

**📖 Extended Documentation & Technical Details:** You can read the full article on how this tool works under the hood and practical use cases at Tux Rincon - TSCM Hunter: Kali Linux Barrido Escuchas.

## ✨ Main Features

*   **Radiofrequency Sweep (SDR):** Detects analog VHF/UHF microphones by measuring anomalous power densities in the electromagnetic spectrum.
*   **Cellular Inspection:** Tracks continuous emissions in common mobile bands (GSM 900/1800) (depending on the SDR hardware's maximum frequency range).
*   **Wi-Fi Hunter (Monitor Mode):** Injects the Wi-Fi card into monitor mode, executes channel hopping, and intercepts raw packets to locate IP cameras and microphones (even with hidden SSIDs) based on their proximity (RSSI).
*   **Bluetooth / BLE Detector:** Logs nearby devices transmitting or waiting to pair using the BlueZ daemon (common in modern portable recorders).
*   **Acoustic Coupling Check (Larsen Effect):** Automatically demodulates the audio signal and plays it through the speakers to force a confirmation beep (feedback loop) if an analog microphone is in the room.
*   **Fine Localization Meter:** Terminal interface with ASCII intensity bars to search with a directional antenna (Geiger counter style).
*   **Configurable Thresholds & Reports:** Fine-grained, independent sensitivity tuning for RF, Cellular, Wi-Fi, and Bluetooth, with detailed log exporting.

## ⚙️ Requirements and Hardware

**Operating System:** Kali Linux 2026+ (or Debian-based distributions oriented towards pentesting).

**Required Hardware:**
*   RTL-SDR USB Dongle (RTL2832U chip recommended).
*   Wi-Fi adapter compatible with Monitor Mode and packet injection.
*   Built-in or USB Bluetooth adapter.
*   Speakers or headphones (for the acoustic coupling test).

## 🚀 Installation

Clone the official repository, navigate to the directory, and run the automatic installation script to prepare the drivers, system rules (udev), and necessary Python libraries.

```bash
git clone https://github.com/beta6/tscm-hunter.git
cd tscm-hunter
sudo chmod +x install.sh
sudo ./install.sh
```

## 🛠️ Usage and Switches

> **Note:** TSCM Hunter must always be run with root privileges due to the permissions required by the RTL-SDR receiver, Wi-Fi monitor mode, and the Bluetooth service.

### Available Parameters

| Switch / Flag | Long Name | Description | Default Value |
| :--- | :--- | :--- | :--- |
| `-s` | `--start` | Start frequency for RF sweep (MHz) | `85.0` |
| `-e` | `--end` | End frequency for RF sweep (MHz) | `110.0` |
| `--trf` | `--trf` | Alert threshold for RF (dB) | `-30.0` |
| `--tcell` | `--tcell` | Alert threshold for cellular bands (dB) | `-30.0` |
| `--twifi` | `--twifi` | Alert RSSI threshold for Wi-Fi (dBm) | `-65.0` |
| `--tbt` | `--tbt` | Alert RSSI threshold for Bluetooth (dBm) | `-65.0` |
| `-d` | `--duration` | Duration of Wi-Fi and Bluetooth scans (seconds) | `10` |
| `-l` | `--locate` | Direct fine localization mode for a specific frequency (MHz) | Disabled |
| `-o` | `--output` | Custom output log file | `tscm_report_DATETIME.log` |
| `-a` | `--all` | Paranoid mode (forces thresholds to minimum to show everything) | `False` |

### Practical Examples

#### 1. Standard Sweep
Start a scan with default values (VHF 85-110 MHz, very close Wi-Fi/BT):
```bash
sudo python3 tscm_hunter.py
```

#### 2. Custom Proximity Threshold Tuning
Require higher signal intensities to trigger the alarm and avoid false positives from neighbors or the street:
```bash
sudo python3 tscm_hunter.py --trf -20 --tcell -25 --twifi -45 --tbt -50
```

#### 3. UHF Band Sweep and Report Generation
Analyze the UHF range from 400 to 450 MHz and save the results to a specific log:
```bash
sudo python3 tscm_hunter.py -s 400.0 -e 450.0 -o boardroom_uhf_report.log
```

#### 4. "Paranoid" Mode (No Filters)
Show absolutely all signals captured in the air, regardless of how weak or distant they are:
```bash
sudo python3 tscm_hunter.py -a -o full_unfiltered_report.log
```

#### 5. Direct Fine Localization
If you know an exact frequency (e.g. 433.92 MHz) and want to connect your directional antenna to triangulate the emitter:
```bash
sudo python3 tscm_hunter.py -l 433.92
```Conversación con Gemini

convert attached file to readme github format markdown
🛠️ Usage and Switches

    Note: TSCM Hunter must always be run with root privileges due to the permissions required by the RTL-SDR receiver, Wi-Fi monitor mode, and the Bluetooth service.

Available Parameters
Switch / Flag	Long Name	Description	Default Value
-s	--start	Start frequency for RF sweep (MHz)	85.0
-e	--end	End frequency for RF sweep (MHz)	110.0
--trf	--trf	Alert threshold for RF (dB)	-30.0
--tcell	--tcell	Alert threshold for cellular bands (dB)	-30.0
--twifi	--twifi	Alert RSSI threshold for Wi-Fi (dBm)	-65.0
--tbt	--tbt	Alert RSSI threshold for Bluetooth (dBm)	-65.0
-d	--duration	Duration of Wi-Fi and Bluetooth scans (seconds)	10
-l	--locate	Direct fine localization mode for a specific frequency (MHz)	Disabled
-o	--output	Custom output log file	tscm_report_DATETIME.log
-a	--all	Paranoid mode (forces thresholds to minimum to show everything)	False
Practical Examples
1. Standard Sweep

Start a scan with default values (VHF 85-110 MHz, very close Wi-Fi/BT):
Bash

sudo python3 tscm_hunter.py

2. Custom Proximity Threshold Tuning

Require higher signal intensities to trigger the alarm and avoid false positives from neighbors or the street:
Bash

sudo python3 tscm_hunter.py --trf -20 --tcell -25 --twifi -45 --tbt -50

3. UHF Band Sweep and Report Generation

Analyze the UHF range from 400 to 450 MHz and save the results to a specific log:
Bash

sudo python3 tscm_hunter.py -s 400.0 -e 450.0 -o boardroom_uhf_report.log

4. "Paranoid" Mode (No Filters)

Show absolutely all signals captured in the air, regardless of how weak or distant they are:
Bash

sudo python3 tscm_hunter.py -a -o full_unfiltered_report.log

5. Direct Fine Localization

If you know an exact frequency (e.g. 433.92 MHz) and want to connect your directional antenna to triangulate the emitter:
Bash

sudo python3 tscm_hunter.py -l 433.92

👨‍💻 Credits and Acknowledgments

This project was designed, developed, and tested under the conceptual and technical supervision of beta6.

For more guides, tutorials, and tools oriented towards Linux, Hacking, and cybersecurity, visit the official community at Tux Rincon.
⚠️ Legal Notice and Disclaimer

This software is provided STRICTLY for educational, research, and authorized auditing purposes.

    Technical Limitations & Hardware Realism: A low-cost RTL-SDR receiver is an excellent learning and initial analysis tool, but it DOES NOT replace a professional laboratory spectrum analyzer or a Non-Linear Junction Detector (NLJD). The tool will generate false positives due to background noise, harmonics from legitimate devices (routers, repeaters, DVB television), or simple tuner overload. Do not rely on this software as the sole means to certify the absolute security of a corporate or government environment.


## 👨‍💻 Credits and Acknowledgments

This project was designed, developed, and tested under the conceptual and technical supervision of **beta6**.

For more guides, tutorials, and tools oriented towards Linux, Hacking, and cybersecurity, visit the official community at Tux Rincon.

## ⚠️ Legal Notice and Disclaimer

**This software is provided STRICTLY for educational, research, and authorized auditing purposes.**

*   **Technical Limitations & Hardware Realism:** A low-cost RTL-SDR receiver is an excellent learning and initial analysis tool, but it DOES NOT replace a professional laboratory spectrum analyzer or a Non-Linear Junction Detector (NLJD). The tool will generate false positives due to background noise, harmonics from legitimate devices (routers, repeaters, DVB television), or simple tuner overload. Do not rely on this software as the sole means to certify the absolute security of a corporate or government environment.
*   **Authorized Use and Legal Compliance:** Intercepting wireless traffic (Wi-Fi monitor mode) and monitoring the radio frequency spectrum is regulated by law in most countries. Run this tool only on your own systems and properties, or in environments where you have the explicit, written authorization of the owner.
*   **Disclaimer of Liability:** Neither the author (beta6) nor Tux Rincon are responsible for any damage, harm, loss of privacy, or legal penalty arising from the improper use of this software. The knowledge acquired must be used ethically and legally.


