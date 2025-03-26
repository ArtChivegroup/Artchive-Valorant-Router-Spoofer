# ⚡ Artchive Valorant Router Spoofer

A modern GUI tool that spoofs your network adapter to simulate a new router identity — useful for bypassing **Van Reconstruction** in Valorant, especially when **Secure Boot** and **TPM 2.0** are disabled.

🔒 Designed to help you play again after router-based HWID bans.

> Built with ❤️ by **moch dimas almahtar**

---

## ✨ Features

- ✅ Random, valid MAC address spoofing
- ✅ Real adapter registry detection (safe spoof)
- ✅ TTL + MTU matching WARP/WireGuard behavior
- ✅ Cloudflare DNS (1.1.1.1 / 1.0.0.1)
- ✅ Modern GUI (dark theme, live status)
- ✅ One-click ON/OFF toggle
- ✅ Adapter auto-disable/enable
- ✅ Progress meter + clean log output


---

## 🖥 Requirements

### 🐍 If using Python:
```
pip install ttkbootstrap wmi pillow==9.5.0
```

- `ttkbootstrap` – for modern dark-mode GUI  
- `wmi` – for detecting real adapter info  
- `pillow==9.5.0` – compatible with Meter widget  
- `pywin32` – already included in most Windows Python installations

### ⚠ Important:
- Always run `warp_toggle.py` with **Administrator privileges**
- MAC spoofing requires elevated access to the Windows Registry

---

## 📦 If using EXE version:
- Run EXE as **Administrator**
- You must install [`WinPcap_4_1_3.exe`](https://github.com/ArtChivegroup/Artchive-Valorant-Router-Spoofer/raw/refs/heads/main/WinPcap_4_1_3.exe) beforehand

---

## 🚀 How to Use

1. Launch the tool as Administrator
2. Select your active adapter (Ethernet / Wi-Fi)
3. Click **Spoof ON**
4. Wait for the status:  
   ```
   ✔ Success! Ready to play Valorant
   ```
5. Launch Valorant and enjoy 🎮
6. Once you're done, click **Spoof OFF** to reset your network settings

---

## 💡 Pro Tips

- Works great on:
  - Realtek LAN adapters
  - USB WiFi dongles
  - TP-Link & Tenda cards
- Best results after system restart
- Can be used before each Valorant session
- Does not rely on VPN or Cloudflare WARP — this is **100% local**

---

[Download For Windows](https://github.com/ArtChivegroup/Artchive-Valorant-Router-Spoofer/releases/download/nightly-20250324-1956/Artchive-Valorant-Router-Spoofer.exe)

## ☕ Buy Me a Coffee

If this project helped you get back in the game...

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/dmzartchive)

Every sip keeps the code clean and the bypass smoother 😎

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `warp_toggle.py` | Main spoofing script |
| `warp_config.json` | Config file to save state & adapter selection |
| `README.md` | This documentation |

---

## 🧠 Legal Note

This tool is provided for educational purposes only. Use it responsibly and at your own risk.

---

💼 Made by: **moch dimas almahtar**  
