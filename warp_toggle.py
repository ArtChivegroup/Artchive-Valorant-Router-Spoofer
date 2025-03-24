import os
import json
import random
import subprocess
import time
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Combobox, Button, Label, Meter
import winreg
import wmi

CONFIG_FILE = "warp_config.json"

# --- REGISTRY HELPERS ---
def get_registry_path(adapter_name):
    c = wmi.WMI()
    try:
        for nic in c.Win32_NetworkAdapter():
            if nic.NetConnectionID == adapter_name:
                net_id = nic.GUID
                break
        else:
            return None

        base_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as key:
            for i in range(100):
                try:
                    subkey = f"{i:04}"
                    with winreg.OpenKey(key, subkey) as sk:
                        val, _ = winreg.QueryValueEx(sk, "NetCfgInstanceId")
                        if val == net_id:
                            return os.path.join(base_path, subkey)
                except:
                    continue
    except:
        return None

# --- NETWORK SETUP ---
def get_adapters():
    result = subprocess.check_output('netsh interface show interface', shell=True).decode()
    lines = result.splitlines()[3:]
    adapters = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 4:
            name = " ".join(parts[3:])
            adapters.append(name)
    return adapters

def random_mac():
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    mac[0] = (mac[0] & 0xFE) | 0x02
    return '-'.join(f"{b:02X}" for b in mac)

def get_current_mac(adapter_name):
    result = subprocess.check_output("getmac /v /fo list", shell=True).decode()
    adapter_section = result.split("Connection Name: ")
    for section in adapter_section:
        if adapter_name in section:
            for line in section.splitlines():
                if "Physical Address" in line:
                    return line.split(":")[-1].strip()
    return "UNKNOWN"

def disable_adapter(adapter_name):
    subprocess.run(f'netsh interface set interface name="{adapter_name}" admin=disable', shell=True)

def enable_adapter(adapter_name):
    subprocess.run(f'netsh interface set interface name="{adapter_name}" admin=enable', shell=True)

def wait_for_adapter_up(adapter_name, timeout=10):
    for _ in range(timeout):
        result = subprocess.check_output('netsh interface show interface', shell=True).decode()
        if adapter_name in result and 'Connected' in result:
            return True
        time.sleep(1)
    return False

def spoof_mac(adapter_name, new_mac):
    reg_path = get_registry_path(adapter_name)
    if not reg_path:
        return False
    reg_mac = new_mac.replace("-", "")
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, reg_mac)
        disable_adapter(adapter_name)
        time.sleep(2)
        enable_adapter(adapter_name)
        return True
    except:
        return False

def reset_mac(adapter_name):
    reg_path = get_registry_path(adapter_name)
    if not reg_path:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "NetworkAddress")
        disable_adapter(adapter_name)
        time.sleep(2)
        enable_adapter(adapter_name)
        return True
    except:
        return False

def set_mtu(adapter_name, mtu):
    subprocess.run(f'netsh interface ipv4 set subinterface "{adapter_name}" mtu={mtu} store=persistent', shell=True)

def set_ttl(ttl_value):
    subprocess.run(f'reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters /v DefaultTTL /t REG_DWORD /d {ttl_value} /f', shell=True)

def clear_ttl():
    subprocess.run(f'reg delete HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters /v DefaultTTL /f', shell=True)

def set_dns(adapter_name):
    subprocess.run(f'netsh interface ip set dns name="{adapter_name}" static addr=1.1.1.1', shell=True)
    subprocess.run(f'netsh interface ip add dns name="{adapter_name}" addr=1.0.0.1 index=2', shell=True)

def reset_dns(adapter_name):
    subprocess.run(f'netsh interface ip set dns name="{adapter_name}" source=dhcp', shell=True)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"enabled": False, "adapter": None}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def toggle_spoof(adapter_name, button, status_label, meter):
    config = load_config()
    enabled = config.get("enabled", False)

    if not adapter_name:
        messagebox.showerror("Error", "Please select a network adapter.")
        return

    meter.configure(amountused=20)
    status_label.config(text="[●] Please wait...")
    status_label.update_idletasks()

    if not enabled:
        spoofed_mac = random_mac()
        status_label.config(text="[●] Disabling adapter...")
        if not spoof_mac(adapter_name, spoofed_mac):
            status_label.config(text="[✘] Failed to spoof MAC address!")
            meter.configure(amountused=0)
            return

        status_label.config(text="[●] Waiting for adapter to reconnect...")
        meter.configure(amountused=50)
        if not wait_for_adapter_up(adapter_name):
            status_label.config(text="[✘] Adapter failed to reconnect!")
            meter.configure(amountused=0)
            return

        set_mtu(adapter_name, 1420)
        set_ttl(128)
        set_dns(adapter_name)
        current_mac = get_current_mac(adapter_name)
        config["enabled"] = True
        config["adapter"] = adapter_name
        config["mac"] = spoofed_mac
        button.config(text="🛑 Spoof OFF", bootstyle="danger")
        status_label.config(text=f"[✔] Success! Ready to play Valorant (MAC: {current_mac})")
        meter.configure(amountused=100)

    else:
        status_label.config(text="[●] Resetting network settings...")
        if not reset_mac(adapter_name):
            status_label.config(text="[✘] Failed to reset MAC address!")
            meter.configure(amountused=0)
            return

        if not wait_for_adapter_up(adapter_name):
            status_label.config(text="[✘] Failed to reactivate adapter!")
            meter.configure(amountused=0)
            return
        set_mtu(adapter_name, 1500)
        clear_ttl()
        reset_dns(adapter_name)
        current_mac = get_current_mac(adapter_name)
        config["enabled"] = False
        config["mac"] = None
        button.config(text="✅ Spoof ON", bootstyle="success")
        status_label.config(text=f"[!] Default restored (MAC: {current_mac})")
        meter.configure(amountused=0)

    save_config(config)

def launch_gui():
    config = load_config()
    style = Style("cyborg")
    root = style.master
    root.title("🔥 Artchive Spoofer - Valorant Router Spoof")
    root.geometry("660x500")
    root.resizable(False, False)

    Label(root, text="Select Network Adapter:", font=("Segoe UI", 10, "bold")).pack(pady=10)
    adapters = get_adapters()
    adapter_var = tk.StringVar()
    adapter_combo = Combobox(root, textvariable=adapter_var, values=adapters, state="readonly", width=35)
    adapter_combo.pack(pady=5)
    if config.get("adapter") in adapters:
        adapter_combo.set(config["adapter"])

    status_label = Label(root, text="[INFO] Default network. Click ON to spoof.", font=("Segoe UI", 9, "italic"))
    status_label.pack(pady=10)

    meter = Meter(root, bootstyle="info", subtext="Spoof Progress", interactive=False)
    meter.configure(amounttotal=100, amountused=0)
    meter.pack(pady=5)

    toggle_button = Button(
        root,
        text="✅ Spoof ON" if not config.get("enabled", False) else "🛑 Spoof OFF",
        bootstyle="success" if not config.get("enabled", False) else "danger",
        command=lambda: toggle_spoof(adapter_combo.get(), toggle_button, status_label, meter)
    )
    toggle_button.pack(pady=10)

    Label(root, text="by moch dimas almahtar", font=("Segoe UI", 8, "italic")).pack(side="bottom", pady=5)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
