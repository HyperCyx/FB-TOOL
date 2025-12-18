# 🎯 FB RECOVERY BOT - Professional Edition

## ✨ Features

**COMPLETE AUTOMATED SOLUTION**
- ✅ Facebook Account Recovery Automation
- ✅ **Professional License System** with online verification
- ✅ **Advanced Anti-Debug Protection** (x64dbg, OllyDbg, IDA Pro)
- ✅ Embedded Proxy System (auto-start)
- ✅ Cross-platform (Windows/Linux/Mac)
- ✅ Multilingual button detection (10+ languages)
- ✅ Real-time statistics tracking
- ✅ Custom proxy support with caching
- ✅ Modern Material Design UI
- ✅ **Intelligent Tab Tracking System**
- ✅ **Auto-close idle tabs after 30s**
- ✅ **Unique Tab IDs in logs**
- ✅ **Standalone EXE Builder** (no dependencies)

## 📁 Project Structure

```
FB-TOOL/
├── FB_Recovery_Bot_Complete.py  ← 🎯 Main Application
├── license_manager.py           ← License verification & API
├── license_ui.py                ← License activation UI
├── protection.py                ← Anti-debug protection system
├── build_exe.py                 ← Standalone EXE builder
├── .gitignore                   ← Git configuration
└── README.md                    ← This file (you are here)
```

## 🚀 Quick Start

### Option 1: Run Python Script (Development)

**1. Install Python** (3.8+) from [python.org](https://www.python.org/)
   - ✅ Check "Add Python to PATH" during installation

**2. Install Dependencies**
```bash
# Windows
pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip requests psutil

# Linux/Mac
pip3 install selenium webdriver-manager customtkinter CTkMessagebox pyperclip requests psutil
```

**3. Run the Bot**
```bash
# Windows
python FB_Recovery_Bot_Complete.py

# Linux/Mac
python3 FB_Recovery_Bot_Complete.py
```

**4. Enter License Key**
   - License activation window appears on first launch
   - Enter your license key
   - License saves automatically
   - Bot launches immediately after verification

---

### Option 2: Build Standalone EXE (Distribution)

Create a standalone executable with **NO dependencies required**:

**Windows:**
```cmd
python build_exe.py
```

**Linux/Mac:**
```bash
python3 build_exe.py
```

**Output:**
- `dist/FB_Recovery_Bot` (Linux: 35 MB)
- `dist/FB_Recovery_Bot.exe` (Windows: 60-90 MB)
- Includes: Python runtime + all dependencies + your code
- **No installation needed** - just run the executable!

**Distribution Package:**
- `FB_Recovery_Bot_Distribution/` - Ready to share
- `FB_Recovery_Bot_Distribution_v1.0_[Platform].zip` - Compressed archive

---

### Option 3: Use Pre-built Executable (End Users)

If you have the executable:
```bash
# Linux
chmod +x FB_Recovery_Bot
./FB_Recovery_Bot

# Windows
FB_Recovery_Bot.exe  (double-click)
```

**No Python, no pip, no dependencies - just run!**

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

## 📊 Live Statistics

The bot tracks and displays real-time metrics:

- **📦 Total Numbers**: Numbers in processing queue
- **✅ OTP Sent**: Successfully sent SMS/OTP count
- **❌ No Account**: Numbers without Facebook accounts

## 🌍 Multilingual Support

Auto-detects buttons in **10+ languages**:
- English, Bengali (বাংলা), Hindi (हिंदी)
- Arabic (العربية), Spanish, French
- German, Portuguese, Indonesian, Chinese (中文)

No more "button not found" errors on non-English Facebook!

## 🔒 License & Protection System

### License Verification
Professional online license system with modern UI:

**Features:**
- ✅ **Beautiful Activation UI**: Modern light theme (500x420)
- ✅ **Online Verification**: Real-time API validation
- ✅ **Auto-Save**: License saved automatically (hidden file)
- ✅ **Silent Auto-Launch**: No window if already licensed
- ✅ **Device Binding**: License tied to specific machine
- ✅ **Multi-device Support**: Track active devices per license
- ✅ **Expiration Dates**: Automatic expiry checking
- ✅ **Clear Error Messages**: Detailed error explanations

**First Launch:**
1. License activation window appears
2. Enter your license key
3. Click "Activate License"
4. System verifies with license server
5. License saves automatically
6. Bot launches immediately

**Subsequent Launches:**
- Checks saved license silently in background
- Auto-launches if valid
- Shows activation window only if expired/invalid

**License Storage:**
- Hidden file: `~/.fb_recovery_license`
- Windows: Hidden attribute + dot-prefix
- Linux/Mac: Dot-prefix (invisible)

### Anti-Debug Protection

**Advanced Security System:**
- 🛡️ **20+ Debugger Detection**: x64dbg, OllyDbg, IDA Pro, Cheat Engine, etc.
- 🛡️ **VM Detection**: VMware, VirtualBox, QEMU
- 🛡️ **Timing Attack Prevention**: Detects code stepping
- 🛡️ **Process Monitoring**: Scans running processes
- 🛡️ **Background Monitoring**: Checks every 2-3 seconds
- 🛡️ **Silent Exit**: No error messages on violation
- 🛡️ **Integrated**: Runs at startup and license check

**Protection Flow:**
1. Initializes before any code execution
2. Checks for attached debuggers (Windows API/Linux TracerPid)
3. Scans all running processes for known debuggers
4. Detects virtual machine environments
5. Monitors continuously in background thread
6. Silent exit if any threat detected (no traces for attackers)

**Makes License Bypass Nearly Impossible:**
- Can't attach debuggers without detection
- Can't step through code (timing detection)
- Can't use common reverse engineering tools
- Silent failure confuses attackers
- Multiple overlapping detection layers

### Configuration

**License API Setup:**
Edit `license_manager.py`:
```python
SERVER_API_KEY = "your_api_key_here"
PRODUCT_ID = "your_product_id"
LICENSE_API_URL = "https://your-server.com/api/verifyLicense"
```

**Current Configuration:**
- API: `https://licencess.netlify.app/api/verifyLicense`
- API Key: `lg_server_8fd7679cfb1f4708a876e6fb1f70f9d5`
- Product ID: `prod_ea740f0d`

## �🔧 Key Features

### 🌐 Proxy System
- ✅ **Custom Proxy Input**: Enter your own proxy with caching
- ✅ **IP Display**: Shows current/proxy IP in real-time
- ✅ **Auto-Start**: Proxy starts automatically when enabled
- ✅ **Proper Shutdown**: Complete cleanup when disabled
- ✅ **Format**: `host:port:username:password`

### 🎨 Modern Interface
- ✅ Material Design with CustomTkinter
- ✅ Real-time statistics dashboard
- ✅ Progress tracking with live updates
- ✅ Activity log with color-coded messages
- ✅ Headless mode for background operation

### ⚡ Automation
- ✅ Multi-window processing (2-30 concurrent)
- ✅ Auto phone number input
- ✅ SMS recovery automation
- ✅ "No account" auto-detection & skip
- ✅ Success tracking with copy button

### 🔒 Smart Detection
- ✅ Auto-detects "No search result" pages
- ✅ Closes failed attempts immediately
- ✅ Handles timeout with retry logic
- ✅ Proxy connection validation

## 🎮 How to Use

### 1. Enter Phone Numbers
- One per line in the input box
- Format: `01234567890` or `+8801234567890`

### 2. Configure Proxy (Optional)
- Toggle **"Custom Proxy Server"** to ON
- Enter proxy: `host:port:username:password`
- Example: `proxy.example.com:4950:user123:pass456`
- Proxy is saved and loaded automatically

### 3. Configure Settings
- **Concurrent Windows**: 2-30 browsers (3-5 recommended)
- **Headless Mode**: Hide browser windows
- **IP Display**: Monitor current/proxy IP

### 4. Start Processing
- Click **"▶️ START BOT"**
- Watch live statistics update
- Monitor activity log for progress

### 5. View Results
- Success numbers appear in green result box
- Click **"📄 COPY"** to copy results
- Use **"⏹️ STOP"** to halt anytime

### 6. Monitor Tab Activity
- **Active Tabs Display**: Shows total tabs (Working/Idle)
- **Unique Tab IDs**: Each tab has unique ID in logs
- **Auto-close Idle Tabs**: Tabs idle for >30s are auto-closed
- **Global Monitor**: Checks all tabs every 10 seconds

## 🔧 Troubleshooting

### Common Issues

**"Module not found" Error**
```bash
pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip
```

**"Port 8889 already in use"**
```bash
# Windows
netstat -ano | findstr :8889
taskkill /F /PID <number>

# Linux/Mac
lsof -ti:8889 | xargs kill -9
```

**Chrome Not Opening**
```bash
pip install --upgrade selenium webdriver-manager
```

**Buttons Not Found (Facebook UI)**
- Bot now supports 10+ languages automatically
- Check internet connection
- Try direct mode (proxy OFF) first

**Proxy Not Connecting**
- Verify proxy format: `host:port:user:pass`
- Check proxy credentials
- Wait 3 seconds for initialization
- Look for "Proxy connected! IP: xxx" in log

**Tabs Not Closing**
- All tabs now close automatically (success, failure, timeout, or error)
- No need for manual intervention
- Check logs for: "❌ [Issue] - closing tab"
- Idle tabs (30s+) are auto-closed by global monitor

## 💡 Advanced Features

### Proxy Caching System
- Proxy saved to `~/.fb_bot_proxy_cache`
- Auto-loads on application restart
- No need to re-enter proxy credentials

### Smart Retry Logic
- 3 retry attempts for proxy connection
- 2 retry attempts for Facebook page loading
- Automatic timeout handling (60s for proxy, 30s direct)

### Enhanced Timeouts
- **Proxy Mode**: 60-second page load timeout
- **Direct Mode**: 30-second page load timeout
- **Per-tab Timeout**: 60 seconds (1 minute) max execution time
- **Global Monitor**: Checks every 5 seconds, auto-closes idle tabs
- **Rate Limiting**: 2-second delay between instances (proxy mode)

### Intelligent Tab Tracking System 🆔
- **Unique Tab IDs**: Each browser tab gets unique ID (Tab #1, Tab #2, etc.)
- **Activity Monitoring**: Tracks working/idle/stopped status for each tab
- **1-Minute Timeout**: Each tab has 60 seconds max execution time
- **Auto-close Idle Tabs**: Tabs with no activity for 60+ seconds are automatically closed
- **Global Checker**: Background thread checks all tabs every 5 seconds
- **Automatic Closure**: All tabs close automatically on success, failure, timeout, or error
- **Live Statistics**: Real-time display of total tabs, working tabs, and idle tabs
- **Smart Logging**: All log messages show Tab ID for easy tracking
  ```
  🆔 Tab #3 (01234567890): 🔵 Loading Facebook recovery page...
  🆔 Tab #3 (01234567890): ✅ SMS sent successfully!
  🆔 Tab #3 (01234567890): ⏱️ Timeout after 62s - closing tab
  ```

### Tab Lifecycle Management
1. **Tab Registration**: Each tab gets unique ID when created
2. **Activity Tracking**: Updates timestamp on every action
3. **Status Updates**: working → idle → stopped states
4. **Automatic Cleanup**: All failed/stuck/timeout tabs are automatically closed
5. **Auto-Close Triggers**:
   - ❌ Input box not found
   - ❌ No account found
   - ❌ Button not found
   - ❌ SMS option not found
   - ⏱️ **Timeout (60 seconds / 1 minute)**
   - ❌ Any error occurs
6. **Success Closure**: Tab closes automatically after OTP sent
7. **Global Monitor**: Checks every 5 seconds, closes idle tabs after 60 seconds

### IP Verification
- Checks system IP on startup
- Verifies proxy IP after connection
- Real-time display updates

## � System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| RAM | 4 GB | 8 GB+ |
| CPU | Dual-core | Quad-core+ |
| OS | Win 10 / Ubuntu 20.04 | Win 11 / Ubuntu 22.04 |
| Network | 5 Mbps | 10+ Mbps |
| Chrome | Latest | Latest |

## 🏗️ Building Standalone Executable

### Quick Build

**Windows:**
```cmd
python build_exe.py
```

**Linux/Mac:**
```bash
python3 build_exe.py
```

### What Happens:
1. ✅ Auto-installs PyInstaller (if needed)
2. ✅ Creates build spec with all dependencies
3. ✅ Compiles Python code to bytecode
4. ✅ Packages everything into ONE file
5. ✅ Creates distribution folder
6. ✅ Generates ZIP archive

**Build Time:** 2-5 minutes

### Output Files

**Executable:**
- Linux: `dist/FB_Recovery_Bot` (35 MB)
- Windows: `dist/FB_Recovery_Bot.exe` (60-90 MB)

**Distribution Package:**
- `FB_Recovery_Bot_Distribution/` folder
- `FB_Recovery_Bot_Distribution_v1.0_[Platform].zip`
- Includes: Executable + README + Documentation

### What's Embedded:

✅ **Your Code:**
- FB_Recovery_Bot_Complete.py (84 KB)
- license_manager.py (4.6 KB)
- license_ui.py (11 KB)
- protection.py (8.0 KB)

✅ **ALL Dependencies (15+ packages):**
- customtkinter, selenium, requests, psutil
- webdriver-manager, pyperclip, pygetwindow
- Pillow, cryptography, certifi, urllib3
- And more...

✅ **Python Runtime:**
- Complete Python 3.12 interpreter
- Standard library
- Dynamic libraries

**Result:** One file with everything! No Python installation needed!

### For End Users:

**Windows:**
- Extract ZIP
- Double-click `FB_Recovery_Bot.exe`
- Enter license key
- Use bot!

**Linux:**
```bash
chmod +x FB_Recovery_Bot
./FB_Recovery_Bot
```

**Requirements for Users:**
- ❌ No Python needed
- ❌ No pip install needed
- ❌ No dependencies needed
- ✅ Just Chrome browser
- ✅ Internet connection

## � Best Practices

1. **Test First**: Start with 2-3 numbers to verify setup
2. **Proxy Testing**: Test direct mode first, then enable proxy
3. **Concurrency**: Start with 3-5 windows, increase gradually
4. **Headless Mode**: Enable only after confirming bot works
5. **Monitor Logs**: Watch activity log for errors/success

## 🔐 Security & Privacy

- ✅ Proxy runs on **localhost:8889** only
- ✅ Not accessible from external network
- ✅ Only affects bot's Chrome instances
- ✅ Proxy cache stored in `~/.fb_bot_proxy_cache`
- ✅ Auto-cleanup on application exit

## 📞 Support

### Quick Checks
- Python 3.8+ installed with PATH configured
- All dependencies installed via pip
- Google Chrome browser installed and updated
- Internet connection active

### Common Solutions
- Try direct mode (proxy OFF) first
- Check activity log for detailed error messages
- Restart bot if proxy won't stop
- Clear cache: delete `~/.fb_bot_proxy_cache`

---

## 🎯 Summary

### Single File Solution
- **File**: `FB_Recovery_Bot_Complete.py` (~45KB)
- **Features**: Bot + Proxy + Statistics + Multilingual
- **Platforms**: Windows 10/11, Linux, macOS

### Quick Commands
```bash
# Windows
python FB_Recovery_Bot_Complete.py

# Linux/Mac
python3 FB_Recovery_Bot_Complete.py

# Build EXE
BUILD_EXE.bat
```

---

**Version**: All-In-One Edition 2025  
**License**: Personal Use  
**Platform**: Cross-Platform

🎉 **Happy Recovery!**
