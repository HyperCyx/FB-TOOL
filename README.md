# 🎯 FB RECOVERY BOT - ALL-IN-ONE EDITION

## ✨ Features

**ONE FILE = EVERYTHING!**
- ✅ Bot + Embedded Proxy in single file
- ✅ Auto-start proxy system
- ✅ Cross-platform (Windows/Linux/Mac)
- ✅ Multilingual button detection (10+ languages)
- ✅ Real-time statistics tracking
- ✅ Custom proxy support with caching
- ✅ Professional Material Design UI
- ✅ **Intelligent Tab Tracking System**
- ✅ **Auto-close idle tabs after 30s**
- ✅ **Unique Tab IDs in logs**
- ✅ **Live tab monitoring (Working/Idle)**

## 📁 Project Structure

```
FB-TOOL/
├── FB_Recovery_Bot_Complete.py  ← 🎯 RUN THIS FILE
├── build_exe.py                 ← Windows EXE builder
├── BUILD_EXE.bat                ← One-click EXE build
└── README.md                    ← This file
```

## 🚀 Quick Start

### Windows Installation

1. **Install Python** (3.8+) from [python.org](https://www.python.org/)
   - ✅ Check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```cmd
   pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip
   ```

3. **Run the Bot**
   ```cmd
   python FB_Recovery_Bot_Complete.py
   ```
   Or simply **double-click** the file!

### Linux/Mac Installation

```bash
# 1. Install dependencies
pip3 install selenium webdriver-manager customtkinter CTkMessagebox pyperclip

# 2. Run the bot
python3 FB_Recovery_Bot_Complete.py
```

### Building Windows EXE

Create a standalone executable that runs without Python:

```cmd
# Easy way - double-click
BUILD_EXE.bat

# Or use Python
python build_exe.py
```

Output: `dist/FB_Recovery_Bot.exe` (~80-120 MB)

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

## 🔧 Key Features

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

## 🏗️ Building Windows EXE

### Quick Build
```cmd
BUILD_EXE.bat
```

### Manual Build
```bash
pip install pyinstaller
python build_exe.py
```

### Output
- **File**: `dist/FB_Recovery_Bot.exe`
- **Size**: ~80-120 MB (all dependencies included)
- **Portable**: Runs on any Windows 10/11 without Python

### Distribution Package
- Executable + Documentation
- ZIP archive ready to share
- No installation required for end users

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
