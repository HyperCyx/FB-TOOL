# 🎯 FB RECOVERY BOT - ALL-IN-ONE EDITION

## ✨ What's New in This Version

**ONE FILE = EVERYTHING!**
- ✅ Bot + Proxy combined in single file
- ✅ Auto-start embedded proxy
- ✅ Cross-platform (Windows/Linux/Mac)
- ✅ No external dependencies (fluxy.py not needed)
- ✅ Clean project structure

## 📁 Your Complete Project

```
FB-TOOL/
├── FB_Recovery_Bot_Complete.py  ← 🎯 RUN THIS FILE (32 KB)
├── README.md                    ← This file
├── QUICKSTART.md                ← Quick reference guide
├── README_WINDOWS.md            ← Windows-specific guide
└── CHANGES_SUMMARY.md           ← Technical details
```

## 🚀 Installation & Usage

### Windows
```cmd
# 1. Install Python from python.org (check "Add to PATH")
# 2. Install packages
pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip

# 3. Run the bot (double-click or command line)
python FB_Recovery_Bot_Complete.py
```

### Linux/Mac
```bash
# 1. Install packages
pip3 install selenium webdriver-manager customtkinter CTkMessagebox pyperclip

# 2. Run the bot
python3 FB_Recovery_Bot_Complete.py
```

## 🌐 Embedded Proxy System

### How It Works
```
┌─────────────────────────────────────────────────────┐
│  1. Toggle proxy ON in the GUI                      │
│  2. Click START                                     │
│  3. Proxy auto-starts in background thread          │
│  4. Chrome uses localhost:8889                      │
│  5. Proxy handles authentication automatically      │
│  6. No popups! No separate files!                   │
└─────────────────────────────────────────────────────┘
```

### Pre-configured Proxy
```
Upstream: c5dc26dff0213e3f.abcproxy.vip:4950
User: abc5650020_kaqz-zone-abc-region-SL
Pass: 98459013
Local Port: 8889 (auto-bound)
```

## ✅ Features

### All-In-One
- ✅ Proxy code embedded (no fluxy.py needed)
- ✅ Auto-start when proxy toggle ON
- ✅ Auto-stop when app closes
- ✅ Single file deployment

### Cross-Platform
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS
- ✅ No platform-specific code

### Modern GUI
- ✅ Material Design with CustomTkinter
- ✅ Live statistics
- ✅ Progress tracking
- ✅ Activity log
- ✅ Headless mode support

### Automation
- ✅ Multi-window (up to 30 concurrent)
- ✅ Auto phone number input
- ✅ SMS recovery automation
- ✅ Success tracking
- ✅ Copy results button

## 🎮 Quick Start

1. **Enter Phone Numbers**
   - One per line in the text box
   - Format: 01234567890

2. **Configure Settings**
   - **Concurrent Windows**: How many browsers (3-30)
   - **Proxy Toggle**: ON = use proxy, OFF = direct
   - **Headless Mode**: Hide browser windows

3. **Start Bot**
   - Click **"START BOT"** button
   - Watch activity log for progress
   - Successful numbers appear in green box

4. **Copy Results**
   - Click **"COPY"** to copy successful numbers
   - Use **"STOP"** to halt bot anytime

## 🔧 What Changed from Previous Version

### Removed Files (Cleanup)
```
❌ fluxy.py (embedded in main file)
❌ local_proxy.py (replaced with embedded code)
❌ firefox_proxy_auth.py (not needed)
❌ test_*.py (all test files)
❌ proxy_relay.py (old version)
❌ take_screenshot.py (utility)
❌ YASWIN FB BOT Ultra (1).py (old version)
```

### New Single File
```
✅ FB_Recovery_Bot_Complete.py (32 KB)
   - Main bot code
   - Embedded proxy server
   - Auto-start management
   - Cross-platform compatibility
   - Modern GUI
```

## 💡 Technical Details

### Embedded Proxy Architecture
```python
# Proxy runs in background thread
def start_embedded_proxy_server():
    # Socket server on localhost:8889
    # Handles HTTP/HTTPS via CONNECT
    # Injects authentication headers
    # Bidirectional forwarding
    
# Auto-start on proxy toggle
if proxy_enabled:
    start_local_proxy()  # Thread-based
```

### Cross-Platform Compatibility
```python
# Platform detection
system = platform.system()  # "Windows" or "Linux" or "Darwin"

# Python command
python_cmd = "python" if system == "Windows" else sys.executable

# Window hiding
if system == "Windows":
    subprocess.CREATE_NO_WINDOW
```

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.7+ | 3.10+ |
| RAM | 4 GB | 8 GB |
| CPU | Dual-core | Quad-core |
| OS | Win 10 / Ubuntu 18.04 | Win 11 / Ubuntu 22.04 |
| Network | 5 Mbps | 10+ Mbps |

## 🔍 Troubleshooting

### "Module not found"
```bash
pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip
```

### "Port 8889 already in use"
```bash
# Windows
netstat -ano | findstr :8889
taskkill /F /PID <number>

# Linux
netstat -tlnp | grep 8889
kill <PID>
```

### "Chrome not opening"
```bash
pip install --upgrade selenium webdriver-manager
```

### Proxy not working
1. Make sure proxy toggle is **ON**
2. Check activity log for proxy start message
3. Try with proxy **OFF** first to test bot
4. Verify internet connection

## 📝 Usage Tips

1. **Test First**: Start with 2-3 numbers to verify everything works
2. **Proxy Toggle**: Test with OFF first, then enable proxy
3. **Concurrent Windows**: Start with 3-5, increase gradually
4. **Hidden Mode**: Only enable after confirming bot works
5. **Activity Log**: Watch for errors and success messages

## 🎉 Benefits of All-In-One Version

### For Users
- ✅ **Simplicity**: Just one file to run
- ✅ **Easy Deployment**: Copy one file, done
- ✅ **No Dependencies**: No fluxy.py needed
- ✅ **Auto-Everything**: Proxy starts automatically

### For Developers
- ✅ **Maintainability**: One file to update
- ✅ **Cleaner**: No scattered files
- ✅ **Portable**: Works anywhere Python runs
- ✅ **Professional**: Clean project structure

## 🔐 Security Notes

- ✅ Proxy runs on **localhost only** (127.0.0.1)
- ✅ Not accessible from network
- ✅ Only affects bot's Chrome instances
- ✅ Credentials embedded (change if needed)
- ✅ Auto-cleanup on exit

## 📞 Support

### Check These First
1. ✅ Python installed correctly
2. ✅ All packages installed
3. ✅ Chrome browser installed
4. ✅ Internet connection working

### Still Issues?
1. Read QUICKSTART.md for quick reference
2. Check README_WINDOWS.md for Windows-specific help
3. Run with proxy OFF to isolate issues
4. Check activity log for error messages

---

## 🎯 Summary

**You now have everything in ONE file!**

- File: `FB_Recovery_Bot_Complete.py`
- Size: 32 KB
- Features: Bot + Proxy + Auto-Start + Cross-Platform
- Ready: Just run it!

**Windows**: `python FB_Recovery_Bot_Complete.py`  
**Linux/Mac**: `python3 FB_Recovery_Bot_Complete.py`

---

**Created by**: Yashwin Khan  
**Admin**: Hyper Red  
**Developer**: HYPER RED  
**Version**: All-In-One Edition 2025  
**Platform**: Cross-Platform (Windows/Linux/Mac)  
**License**: Personal Use

🎉 **Happy Recovery!**
