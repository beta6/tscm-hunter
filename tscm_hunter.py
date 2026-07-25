#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import os
import argparse
import threading
import subprocess
import numpy as np
from scipy import signal
import sounddevice as sd
from rtlsdr import RtlSdr
from scapy.all import sniff, Dot11, Dot11Beacon, Dot11ProbeReq
from rich.console import Console
from rich.table import Table
from rich.progress import track
from datetime import datetime

console = Console()
LOG_FILE = f"tscm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
wifi_devices = {}
hopping = True

def write_log(message):
    """Writes messages to the log file."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

def print_step(msg):
    console.print(f"\n[bold cyan][*] {msg}[/bold cyan]")
    write_log(f"[*] {msg}")

def print_success(msg):
    console.print(f"[bold green][+] {msg}[/bold green]")
    write_log(f"[+] {msg}")

def print_warning(msg):
    console.print(f"[bold yellow][!] {msg}[/bold yellow]")
    write_log(f"[!] {msg}")

def print_error(msg):
    console.print(f"[bold red][-] {msg}[/bold red]")
    write_log(f"[-] {msg}")

def init_environment():
    """Checks root permissions (required for SDR and monitor mode)."""
    if os.geteuid() != 0:
        print_error("This script must be run as root (sudo).")
        sys.exit(1)
    console.print("[bold blue]=======================================[/bold blue]")
    console.print("[bold blue]        TSCM HUNTER V2.0 (KALI)        [/bold blue]")
    console.print("[bold blue]=======================================[/bold blue]")
    write_log("Starting TSCM Hunter V2.0")

def setup_wireless():
    """Finds a Wi-Fi card and puts it into monitor mode."""
    print_step("Configuring Wi-Fi interface in monitor mode...")
    try:
        result = subprocess.run(["iw", "dev"], capture_output=True, text=True)
        iface = None
        for line in result.stdout.split('\n'):
            if "Interface" in line:
                iface = line.split(" ")[1]
                break
        
        if not iface:
            print_warning("No Wi-Fi card found. Skipping Wi-Fi scan.")
            return None

        subprocess.run(["airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL)
        subprocess.run(["airmon-ng", "start", iface], stdout=subprocess.DEVNULL)
        
        mon_iface = f"{iface}mon"
        # Check if the monitor interface was created
        check_mon = subprocess.run(["iw", "dev"], capture_output=True, text=True)
        if mon_iface not in check_mon.stdout:
             mon_iface = iface # Sometimes airmon-ng does not rename the interface

        print_success(f"Interface {mon_iface} configured in monitor mode.")
        return mon_iface
    except Exception as e:
        print_error(f"Error configuring Wi-Fi: {e}")
        return None

def channel_hopper(iface):
    """Hops between 2.4GHz Wi-Fi channels to capture all traffic."""
    global hopping
    channels = [1, 6, 11, 2, 7, 3, 8, 4, 9, 5, 10, 12, 13]
    while hopping:
        for ch in channels:
            if not hopping:
                break
            try:
                subprocess.run(["iwconfig", iface, "channel", str(ch)], stderr=subprocess.DEVNULL)
                time.sleep(0.5)
            except:
                pass

def packet_handler(pkt):
    """Processes captured Wi-Fi packets and extracts MAC, SSID, and RSSI."""
    if pkt.haslayer(Dot11):
        if pkt.type == 0 and pkt.subtype == 8: # Beacon frame
            mac = pkt.addr2
            try:
                ssid = pkt.info.decode()
            except:
                ssid = "<Hidden or Corrupted>"
            try:
                rssi = pkt.dBm_AntSignal
            except:
                rssi = -100
                
            if mac not in wifi_devices or rssi > wifi_devices[mac]['rssi']:
                wifi_devices[mac] = {'ssid': ssid, 'rssi': rssi, 'type': 'AP/Beacon'}
                
        elif pkt.type == 0 and pkt.subtype == 4: # Probe Request
            mac = pkt.addr2
            try:
                ssid = pkt.info.decode()
            except:
                ssid = "<General Search>"
            try:
                rssi = pkt.dBm_AntSignal
            except:
                rssi = -100
                
            if mac not in wifi_devices or rssi > wifi_devices[mac]['rssi']:
                wifi_devices[mac] = {'ssid': f"Searching: {ssid}", 'rssi': rssi, 'type': 'Client/Probe'}

def scan_wifi(iface, duration=10):
    """Starts the Wi-Fi scan in a separate thread."""
    global hopping
    print_step(f"Starting Wi-Fi scan (Monitor) for {duration} seconds...")
    hopping = True
    hop_thread = threading.Thread(target=channel_hopper, args=(iface,), daemon=True)
    hop_thread.start()
    
    try:
        sniff(iface=iface, prn=packet_handler, timeout=duration, store=0)
    except Exception as e:
        print_error(f"Error during Wi-Fi sniff: {e}")
        
    hopping = False
    print_success(f"Wi-Fi scan completed. {len(wifi_devices)} devices seen.")

def scan_bluetooth(duration=10):
    """Scans for nearby Bluetooth (Classic/BLE) devices via the system daemon."""
    print_step(f"Starting passive Bluetooth tracking for {duration} seconds...")
    bt_devices = {}
    try:
        # Ensure the Bluetooth adapter is powered on
        subprocess.run(["rfkill", "unblock", "bluetooth"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Start scanning with a built-in timeout
        subprocess.run(["bluetoothctl", "--timeout", str(duration), "scan", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Get discovered devices from BlueZ cache
        result = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith("Device"):
                parts = line.split(" ", 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    
                    # Request detailed info (RSSI) for the device
                    info = subprocess.run(["bluetoothctl", "info", mac], capture_output=True, text=True)
                    rssi = -100 # Default if signal is imperceptible
                    for info_line in info.stdout.split('\n'):
                        if "RSSI:" in info_line:
                            try:
                                rssi = int(info_line.split("RSSI:")[1].strip())
                            except:
                                pass
                    bt_devices[mac] = {'name': name, 'rssi': rssi}
                    
        print_success(f"Bluetooth scan completed. {len(bt_devices)} unique devices seen.")
    except Exception as e:
        print_error(f"Error scanning Bluetooth: {e}")
        
    return bt_devices

def init_sdr():
    """Initializes the RTL-SDR hardware."""
    print_step("Initializing RTL-SDR...")
    try:
        sdr = RtlSdr()
        sdr.sample_rate = 2.048e6  # 2.048 MHz
        sdr.err_ppm = 0
        sdr.gain = 'auto'
        print_success("RTL-SDR detected and successfully configured.")
        return sdr
    except Exception as e:
        print_error(f"Could not initialize the RTL-SDR. Is it plugged in? Error: {e}")
        return None

def find_rf_peaks(sdr, start_freq, end_freq, threshold_db=-30.0):
    """Performs a band sweep looking for anomalous RF peaks (Analog Microphones)."""
    print_step(f"Starting RF sweep ({start_freq/1e6:.1f} MHz - {end_freq/1e6:.1f} MHz)...")
    step = sdr.sample_rate
    current_freq = start_freq
    peaks = []

    while current_freq <= end_freq:
        sdr.center_freq = current_freq
        time.sleep(0.1) # Oscillator stabilization
        samples = sdr.read_samples(1024 * 64)
        
        # Calculate Power Spectral Density (PSD)
        power, freqs = plt_psd(samples, sdr.sample_rate, sdr.center_freq)
        max_idx = np.argmax(power)
        max_pwr = power[max_idx]
        max_freq = freqs[max_idx]

        if max_pwr > threshold_db:
            peaks.append({"freq": max_freq, "power": max_pwr})
            console.print(f"[yellow]>> Peak detected: {max_freq/1e6:.3f} MHz | {max_pwr:.1f} dB[/yellow]")

        current_freq += step

    print_success(f"RF sweep completed. Peaks detected: {len(peaks)}")
    return peaks

def scan_cellular(sdr, threshold_db=-30.0):
    """Scans common GSM/LTE bands for cellular/SIM microphones."""
    print_step("Starting cellular bands scan (GSM 900/1800)...")
    # Approximate common bands (generic downlink/uplink)
    bands = {
        "GSM 900": (890e6, 915e6),
        "DCS 1800": (1710e6, 1785e6) # May fail on generic RTL2832U SDRs (limit ~1.7GHz)
    }
    
    cell_peaks = []
    for band_name, (start, end) in bands.items():
        try:
            sdr.center_freq = start
            print_warning(f"Scanning {band_name} band...")
            # A simplified quick scan in 2MHz chunks
            curr = start
            while curr <= end:
                sdr.center_freq = curr
                time.sleep(0.05)
                samples = sdr.read_samples(1024 * 32)
                power, freqs = plt_psd(samples, sdr.sample_rate, sdr.center_freq)
                max_idx = np.argmax(power)
                if power[max_idx] > threshold_db:
                    cell_peaks.append({"band": band_name, "freq": freqs[max_idx], "power": power[max_idx]})
                curr += sdr.sample_rate
        except Exception as e:
            print_warning(f"Could not scan {band_name} band (SDR hardware limit reached).")
            
    return cell_peaks

def plt_psd(samples, sample_rate, center_freq):
    """Calculates FFT and power of complex samples."""
    fft_data = np.fft.fftshift(np.fft.fft(samples))
    power = 10 * np.log10(np.abs(fft_data)**2 / len(samples))
    freqs = np.linspace(center_freq - sample_rate/2, center_freq + sample_rate/2, len(power))
    return power, freqs

def demodulate_and_play(sdr, target_freq, duration=5):
    """Demodulates NFM and plays audio through speakers to force Larsen Effect (Acoustic Coupling)."""
    sdr.center_freq = target_freq
    audio_sample_rate = 44100
    decimation_rate = int(sdr.sample_rate // audio_sample_rate)
    
    console.print(f"[cyan]Demodulating and injecting audio (Larsen) at {target_freq/1e6:.3f} MHz for {duration}s...[/cyan]")
    
    def audio_callback(outdata, frames, time_info, status):
        try:
            samples = sdr.read_samples(frames * decimation_rate)
            # Simple FM demodulation (phase discriminator)
            phase = np.unwrap(np.angle(samples))
            demodulated = np.diff(phase)
            # Decimation to match audio sample rate
            audio_data = signal.resample(demodulated, frames)
            # Normalization and volume adjustment
            audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data
            outdata[:, 0] = audio_data
        except Exception as e:
            outdata.fill(0)

    try:
        with sd.OutputStream(channels=1, callback=audio_callback, samplerate=audio_sample_rate):
            sd.sleep(duration * 1000)
    except Exception as e:
        print_error(f"Audio error: {e}")

def fine_localization(sdr, target_freq):
    """Displays a real-time RSSI meter to localize the transmitter directionally."""
    sdr.center_freq = target_freq
    console.print("[bold yellow]\n--- FINE LOCALIZATION ACTIVE (Directional Antenna) ---[/bold yellow]")
    console.print("[cyan]Move the antenna. Press Ctrl+C to stop and return to the menu.[/cyan]\n")
    try:
        while True:
            samples = sdr.read_samples(1024 * 16)
            power = 10 * np.log10(np.mean(np.abs(samples)**2))
            
            # Normalize power for the visual bar (e.g. -60 dB to 0 dB)
            bar_len = int(np.clip((power + 60) / 2, 0, 30))
            bar = "█" * bar_len + "▒" * (30 - bar_len)
            color = "green" if power < -30 else ("yellow" if power < -15 else "red")
            
            sys.stdout.write(f"\rPower: [{power:6.1f} dB] | [{color}]{bar}[/{color}]")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n")
        print_success("Fine localization finished.")

def render_ascii_bar(rssi, is_wifi=False):
    """Generates a colored ASCII bar based on RSSI power."""
    if is_wifi:
        # Typical Wi-Fi / BT scale: -90 (weak) to -30 (strong)
        min_r, max_r = -90, -30
    else:
        # Typical RF scale: -60 (weak) to 0 (strong)
        min_r, max_r = -60, 0
        
    width = 20
    # Calculate percentage
    percent = (rssi - min_r) / (max_r - min_r)
    percent = max(0.0, min(1.0, percent)) # Clamp between 0 and 1
    
    filled = int(width * percent)
    empty = width - filled
    
    bar = "█" * filled + "▒" * empty
    
    if percent < 0.4:
        color = "green"
    elif percent < 0.75:
        color = "yellow"
    else:
        color = "red"
        
    return f"[{color}]{bar}[/{color}]", color

def generate_final_report(rf_peaks, cell_peaks, bt_devices, thresholds):
    """Displays all categorized threats with applied thresholds and visual charts."""
    console.print("\n")
    write_log("=== TSCM FINAL REPORT ===")
    
    # 1. RF and Cellular Table
    table_rf = Table(title=f"[bold yellow]DETECTED RF AND CELLULAR ANOMALIES[/bold yellow]", show_lines=True)
    table_rf.add_column("Frequency (MHz)")
    table_rf.add_column("Type")
    table_rf.add_column("Power")
    table_rf.add_column("Proximity Chart", justify="left")

    if not rf_peaks and not cell_peaks:
        table_rf.add_row("-", "None", "-", "No RF/Cellular peaks detected.")
        write_log("No RF or cellular peaks detected.")
    else:
        for p in rf_peaks:
            freq_mhz = p["freq"] / 1e6
            pwr = p["power"]
            bar, color = render_ascii_bar(pwr, is_wifi=False)
            table_rf.add_row(f"{freq_mhz:.3f}", "RF (VHF/UHF)", f"[{color}]{pwr:.1f} dB[/{color}]", bar)
            write_log(f"RF Detected: {freq_mhz:.3f} MHz | {pwr:.1f} dB")
            
        for p in cell_peaks:
            freq_mhz = p["freq"] / 1e6
            pwr = p["power"]
            bar, color = render_ascii_bar(pwr, is_wifi=False)
            table_rf.add_row(f"{freq_mhz:.3f}", p["band"], f"[{color}]{pwr:.1f} dB[/{color}]", bar)
            write_log(f"Cellular Detected: {freq_mhz:.3f} MHz | {p['band']} | {pwr:.1f} dB")

    console.print(table_rf)
    
    # 2. Wi-Fi Table
    console.print("\n")
    table_wi = Table(title=f"[bold green]HIDDEN / SUSPICIOUS WI-FI NETWORKS (Filter > {thresholds['wifi']} dBm)[/bold green]", show_lines=True)
    table_wi.add_column("MAC Address")
    table_wi.add_column("SSID / Type")
    table_wi.add_column("Intensity")
    table_wi.add_column("Proximity Chart", justify="left")
    
    filtered_wifi = {k: v for k, v in wifi_devices.items() if v['rssi'] >= thresholds['wifi']}
    
    if not filtered_wifi:
        table_wi.add_row("-", "-", "-", f"None exceed {thresholds['wifi']} dBm")
        write_log("No Wi-Fi devices above threshold.")
    else:
        for mac, info in sorted(filtered_wifi.items(), key=lambda x: x[1]['rssi'], reverse=True):
            rssi = info['rssi']
            bar, color = render_ascii_bar(rssi, is_wifi=True)
            warning = " [bold red]! CRITICAL (VERY CLOSE) ![/bold red]" if rssi > -45 else ""
            table_wi.add_row(mac, f"{info['ssid']} ({info['type']})", f"[{color}]{rssi} dBm[/{color}]{warning}", bar)
            write_log(f"Wi-Fi Detected: {mac} | {info['ssid']} | {rssi} dBm")

    console.print(table_wi)
    
    # 3. Bluetooth Table
    console.print("\n")
    table_bt = Table(title=f"[bold cyan]NEARBY BLUETOOTH DEVICES (Filter > {thresholds['bt']} dBm)[/bold cyan]", show_lines=True)
    table_bt.add_column("MAC Address")
    table_bt.add_column("Name / ID")
    table_bt.add_column("Intensity")
    table_bt.add_column("Proximity Chart", justify="left")
    
    filtered_bt = {k: v for k, v in bt_devices.items() if v['rssi'] >= thresholds['bt']}
    
    if not filtered_bt:
        table_bt.add_row("-", "-", "-", f"None exceed {thresholds['bt']} dBm")
        write_log("No Bluetooth devices above threshold.")
    else:
        for mac, info in sorted(filtered_bt.items(), key=lambda x: x[1]['rssi'], reverse=True):
            rssi = info['rssi']
            bar, color = render_ascii_bar(rssi, is_wifi=True)
            warning = " [bold red]! CRITICAL (VERY CLOSE) ![/bold red]" if rssi > -55 else ""
            table_bt.add_row(mac, info['name'], f"[{color}]{rssi} dBm[/{color}]{warning}", bar)
            write_log(f"Bluetooth Detected: {mac} | {info['name']} | {rssi} dBm")

    console.print(table_bt)
    print_success(f"Detailed log saved to: {LOG_FILE}")

def main():
    parser = argparse.ArgumentParser(description="TSCM Hunter V2.0 - Comprehensive Microphone Detection (RF, Wi-Fi, BT, Cell)")
    parser.add_argument("-s", "--start", type=float, default=85.0, help="RF start frequency in MHz (e.g. 85.0)")
    parser.add_argument("-e", "--end", type=float, default=110.0, help="RF end frequency in MHz (e.g. 110.0)")
    
    parser.add_argument("--trf", type=float, default=-30.0, help="Power threshold for RF anomalies in dB (e.g. -30.0)")
    parser.add_argument("--tcell", type=float, default=-30.0, help="Power threshold for Cellular bands in dB (e.g. -30.0)")
    parser.add_argument("--twifi", type=float, default=-65.0, help="RSSI threshold for Wi-Fi in dBm (e.g. -65.0)")
    parser.add_argument("--tbt", type=float, default=-65.0, help="RSSI threshold for Bluetooth in dBm (e.g. -65.0)")
    
    parser.add_argument("-d", "--duration", type=int, default=10, help="Duration of Wi-Fi/BT scan in seconds (default 10)")
    parser.add_argument("-l", "--locate", type=float, help="Skip general scan and locate specific frequency (MHz)")
    
    parser.add_argument("-o", "--output", type=str, help="Custom output log file path (e.g. boardroom_report.log)")
    parser.add_argument("-a", "--all", action="store_true", help="Show all detections (ignores configured thresholds)")
    
    args = parser.parse_args()

    # Custom output file configuration
    global LOG_FILE
    if args.output:
        LOG_FILE = args.output

    # Force thresholds to minimum if --all (-a) flag is specified
    if args.all:
        args.trf = -200.0
        args.tcell = -200.0
        args.twifi = -200.0
        args.tbt = -200.0

    init_environment()
    
    # If the user only wants to locate a specific frequency
    if args.locate:
        sdr = init_sdr()
        if sdr:
            fine_localization(sdr, args.locate * 1e6)
            sdr.close()
        sys.exit(0)

    # 1. Wireless Scans (Wi-Fi and Bluetooth)
    wifi_iface = setup_wireless()
    if wifi_iface:
        scan_wifi(wifi_iface, duration=args.duration)

    bt_devices = scan_bluetooth(duration=args.duration)

    # 2. SDR Scans (RF and Cellular)
    rf_peaks = []
    cell_peaks = []
    
    sdr = init_sdr()
    if sdr:
        rf_peaks = find_rf_peaks(sdr, args.start * 1e6, args.end * 1e6, threshold_db=args.trf)
        cell_peaks = scan_cellular(sdr, threshold_db=args.tcell)
        
        # 3. Acoustic Coupling Check (Larsen Effect)
        if rf_peaks:
            print_warning(f"Found {len(rf_peaks)} RF peaks. Starting Larsen Effect check...")
            for i, p in enumerate(rf_peaks):
                freq_mhz = p["freq"] / 1e6
                console.print(f"\n[bold magenta]>> Analyzing peak {i+1}/{len(rf_peaks)}: {freq_mhz:.3f} MHz[/bold magenta]")
                demodulate_and_play(sdr, p["freq"], duration=6)
                
                resp = console.input(f"Fine directional localization for {freq_mhz:.3f} MHz? (y/N): ")
                if resp.lower() == 'y':
                    fine_localization(sdr, p["freq"])

        sdr.close()

    # 4. Unified Final Report
    thresholds = {
        'rf': args.trf,
        'cell': args.tcell,
        'wifi': args.twifi,
        'bt': args.tbt
    }
    generate_final_report(rf_peaks, cell_peaks, bt_devices, thresholds=thresholds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nProcess interrupted by user.")
        sys.exit(0)
