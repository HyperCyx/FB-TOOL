# 🚀 FB RECOVER BOT - Windows Installation Guide

## 📋 Prerequisites

### 1. Install Python
- Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
- ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify installation:
  ```cmd
  python --version
  ```

### 2. Install Chrome Browser
- Download from [google.com/chrome](https://www.google.com/chrome/)

## 📦 Installation Steps

### Step 1: Download the Project
```cmd
cd C:\Users\YourUsername\Desktop
```
Extract the FB-TOOL folder to your Desktop

### Step 2: Install Dependencies
Open Command Prompt as Administrator in the FB-TOOL folder:

```cmd
cd C:\Users\YourUsername\Desktop\FB-TOOL
pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip
```

### Step 3: Verify Files
Make sure you have the main file:
- ✅ `FB_Recovery_Bot_Complete.py` (All-in-one bot with embedded proxy)

## 🚀 Running the Bot

### Option 1: Double-Click
Simply double-click on:
```
FB_Recovery_Bot_Complete.py
```

### Option 2: Command Line
```cmd
cd C:\Users\YourUsername\Desktop\FB-TOOL
python FB_Recovery_Bot_Complete.py
```

## 🌐 Proxy Configuration

### Default Proxy (Pre-configured)
The bot comes with a default proxy:
```
c5dc26dff0213e3f.abcproxy.vip:4950:abc5650020_kaqz-zone-abc-region-SL:98459013
```

### Using Your Own Proxy
Format: `host:port:username:password`

Example:
```
proxy.example.com:8080:myuser:mypass123
```

### How Proxy Works
1. **Embedded Proxy**: The bot has built-in proxy server (no external files needed)
2. **No Authentication Popups**: Proxy handles authentication automatically
3. **Local Only**: Proxy runs on `localhost:8889` (not accessible from network)
4. **Auto-Start**: No manual proxy management needed

### Proxy Toggle
- **ON**: Chrome uses proxy (different IP)
- **OFF**: Chrome uses direct connection (your system IP)

## 🎮 Using the Bot

### 1. Configure Settings
- **Numbers File**: Upload .txt file with phone numbers (one per line)
- **Proxy**: Enter proxy or use default
- **Proxy Toggle**: Turn ON/OFF as needed
- **Hidden Mode**: Hide browser windows

### 2. Start Bot
- Click **"START"** button
- Bot opens multiple Chrome windows
- Each window processes one number
- Success numbers shown in status area

### 3. Stop Bot
- Click **"STOP"** button
- All Chrome windows close automatically

## 🔧 Troubleshooting

### Chrome Not Opening
```cmd
pip install --upgrade selenium webdriver-manager
```

### "python not recognized" Error
- Reinstall Python with "Add to PATH" checked
- OR use full path:
  ```cmd
  C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\python.exe "YASWIN FB BOT Ultra (1).py"
  ```

### Proxy Not Working
1. Check proxy credentials are correct
2. Ensure proxy toggle is **ON**
3. Embedded proxy will auto-start (no manual action needed)

### Port 8889 Already in Use
```cmd
netstat -ano | findstr :8889
taskkill /F /PID <PID_NUMBER>
```

### CustomTkinter Error
```cmd
pip install --upgrade customtkinter
```

## 🎯 Features

### ✅ Windows Compatible
- No Linux-specific dependencies
- Works on Windows 10/11
- Automatic browser management

### ✅ Embedded Proxy System
- Auto-starts when proxy enabled
- Handles HTTPS tunnels
- No authentication popups
- Isolated to configured browsers only

### ✅ Multi-Window Support
- Opens multiple Chrome instances
- Processes numbers concurrently
- Auto-positions windows

### ✅ Modern UI
- CustomTkinter Material Design
- Dark/Light theme support
- Responsive layout

## 📝 File Structure

```
FB-TOOL/
├── FB_Recovery_Bot_Complete.py   ← Main bot (run this - all-in-one)
├── README.md                     ← Main documentation
├── README_WINDOWS.md             ← This file
├── QUICKSTART.md                 ← Quick reference
├── BUILD_GUIDE.md                ← EXE building guide
└── build_exe.py                  ← EXE builder script
```

## 🌍 Platform Support

| Feature | Windows | Linux | Mac |
|---------|---------|-------|-----|
| Main Bot | ✅ | ✅ | ✅ |
| Embedded Proxy | ✅ | ✅ | ✅ |
| Chrome Browser | ✅ | ✅ | ✅ |
| Auto-Start Proxy | ✅ | ✅ | ✅ |
| EXE Builder | ✅ | ❌ | ❌ |
| VNC (Remote Desktop) | ❌ | ✅ | ❌ |

**Note**: VNC features are Linux-only and not needed for Windows users

## 🔐 Security Notes

- ✅ Proxy runs on **localhost only** (127.0.0.1:8889)
- ✅ Not accessible from network
- ✅ Only affects Chrome instances launched by bot
- ✅ Other apps use direct connection
- ✅ Credentials stored locally

## 💡 Tips

1. **Test Proxy**: Turn ON proxy toggle and click START with 1-2 numbers first
2. **Direct Mode**: Turn OFF proxy toggle for testing without proxy
3. **Hidden Mode**: Enable to reduce screen clutter with many windows
4. **Concurrency**: Start with 5-10 windows, increase gradually
5. **Save Numbers**: Keep backup of `numbers.txt` file

## 📞 Support

For issues or questions:
1. Check proxy credentials
2. Verify Python and Chrome are installed
3. Try running with proxy OFF first
4. Check Windows Firewall settings

## 🔄 Updates

To update dependencies:
```cmd
pip install --upgrade selenium webdriver-manager customtkinter CTkMessagebox
```

---
**Created by**: Yashwin Khan  
**Version**: 2025 Premium Edition  
**Platform**: Cross-Platform (Windows/Linux/Mac)
