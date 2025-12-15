# 🏗️ Building Windows EXE - Complete Guide

## Overview

This guide explains how to create a standalone Windows executable (.exe) from the Python bot that can run on any Windows machine without requiring Python installation.

## Prerequisites

### For Building (Development Machine)
- Python 3.8 or higher
- Windows 10/11 (or Windows build environment)
- All bot dependencies installed

### For Running (Target Machine)
- Windows 10/11 (64-bit)
- Google Chrome browser
- No Python required! ✅

## Quick Build - Option 1: Automated Script

### Windows Users

1. **Double-click** `BUILD_EXE.bat`
2. Wait for build to complete (2-5 minutes)
3. Find your executable in `dist/FB_Recovery_Bot.exe`

The batch file automatically:
- Checks Python installation
- Installs PyInstaller if needed
- Builds the executable
- Creates distribution package
- Generates ZIP archive

## Manual Build - Option 2: Python Script

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Run Build Script
```bash
python build_exe.py
```

### Step 3: Locate Executable
```
dist/FB_Recovery_Bot.exe  # Your standalone executable
```

## Manual Build - Option 3: Direct PyInstaller

### For Advanced Users

```bash
# Install PyInstaller
pip install pyinstaller

# Build with spec file
pyinstaller --clean --noconfirm FB_Recovery_Bot.spec

# Or build directly (one-liner)
pyinstaller --onefile --windowed --name="FB_Recovery_Bot" ^
  --hidden-import=customtkinter ^
  --hidden-import=CTkMessagebox ^
  --hidden-import=selenium ^
  --hidden-import=webdriver_manager ^
  FB_Recovery_Bot_Complete.py
```

## Build Configuration

### Spec File Settings

The `FB_Recovery_Bot.spec` file controls the build:

```python
# Window Mode
console=False  # No console window (GUI only)
# Change to True if you want to see debug output

# Optimization
upx=True  # Compress executable (smaller size)

# Hidden Imports (required modules)
hiddenimports=[
    'customtkinter',
    'CTkMessagebox',
    'selenium',
    'webdriver_manager',
    # ... more
]
```

### Customization Options

#### Add Custom Icon
```python
# In spec file
icon='icon.ico'  # Path to your icon file
```

#### Include Additional Files
```python
# In spec file
datas=[
    ('README.md', '.'),
    ('config.ini', '.'),
]
```

#### Change Output Name
```python
# In spec file
name='MyCustomName'
```

## Troubleshooting Build Issues

### Issue: "PyInstaller not found"
```bash
# Solution
pip install pyinstaller
```

### Issue: "Module not found" during build
```bash
# Solution: Install missing module
pip install <module-name>

# Or add to spec file
hiddenimports=['module-name']
```

### Issue: Large EXE file size (>200MB)
```python
# Solution: Enable UPX compression
upx=True  # In spec file

# Or exclude unnecessary packages
excludes=['tkinter', 'matplotlib']  # If not needed
```

### Issue: Antivirus blocks the EXE
**This is normal!** PyInstaller executables are often flagged.

**Solutions:**
1. Add exception in antivirus
2. Sign the executable with code signing certificate
3. Submit to antivirus vendor as false positive

### Issue: Import errors at runtime
```python
# Solution: Add to hiddenimports in spec file
hiddenimports=[
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.support.ui',
    # Add any missing imports here
]
```

## Distribution Package Structure

After building, you'll get:

```
FB_Recovery_Bot_Windows/
├── FB_Recovery_Bot.exe          # Main executable
├── README.txt                    # User guide
├── QUICKSTART.md                # Quick reference
├── PROXY_FEATURES.md            # Proxy documentation
└── PROXY_FIXES.md               # Troubleshooting

FB_Recovery_Bot_Windows_v1.0.zip # Ready to share!
```

## Testing the Executable

### Step 1: Test Locally
```bash
# Run the executable
dist\FB_Recovery_Bot.exe
```

### Step 2: Test on Clean Machine
- Copy to a computer without Python
- Double-click to run
- Verify all features work

### Step 3: Test with Antivirus
- Enable Windows Defender
- Scan the executable
- Add exception if needed

## Multilingual Support

The bot now includes multilingual button detection for:

- **English**: Search, Send, Continue
- **Bengali**: খুঁজুন, পাঠান, চালিয়ে যান
- **Hindi**: खोजें, भेजें, जारी रखें
- **Arabic**: بحث, إرسال, متابعة
- **Spanish**: Buscar, Enviar, Continuar
- **French**: Rechercher, Envoyer, Continuer
- **German**: Suchen, Senden, Weiter
- **Portuguese**: Pesquisar, Enviar, Continuar
- **Indonesian**: Cari, Kirim, Lanjutkan
- **Chinese**: 搜索, 发送, 继续

This fixes the issue where the bot couldn't find buttons in non-English Facebook interfaces.

## Build Performance

| Metric | Value |
|--------|-------|
| Build Time | 2-5 minutes |
| EXE Size | ~80-120 MB |
| Startup Time | 3-5 seconds |
| Dependencies | All included |

## Advanced: Using C++ Wrapper (Optional)

For even smaller executables, you can create a C++ launcher:

### Example: launcher.cpp
```cpp
#include <windows.h>
#include <string>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, 
                   LPSTR lpCmdLine, int nCmdShow) {
    // Launch the Python executable
    ShellExecute(NULL, "open", "FB_Recovery_Bot.exe", 
                 NULL, NULL, SW_SHOW);
    return 0;
}
```

Compile with:
```bash
g++ -o launcher.exe launcher.cpp -mwindows
```

This creates a tiny (20KB) launcher that executes the main Python EXE.

## Continuous Integration (CI)

### GitHub Actions Example

```yaml
name: Build Windows EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python build_exe.py
      - uses: actions/upload-artifact@v2
        with:
          name: FB_Recovery_Bot_Windows
          path: FB_Recovery_Bot_Windows_v1.0.zip
```

## Security Considerations

### Code Signing (Recommended)

To avoid antivirus false positives:

1. **Get Code Signing Certificate**
   - Purchase from CA (Sectigo, DigiCert)
   - Or use self-signed for testing

2. **Sign the Executable**
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com FB_Recovery_Bot.exe
   ```

### Obfuscation (Optional)

Protect your code from decompilation:

```bash
pip install pyarmor
pyarmor pack FB_Recovery_Bot_Complete.py
```

## Distribution Checklist

Before sharing your executable:

- [ ] Test on clean Windows 10/11 machine
- [ ] Verify Chrome compatibility
- [ ] Test proxy functionality
- [ ] Check antivirus compatibility
- [ ] Include README.txt
- [ ] Add version number
- [ ] Create ZIP archive
- [ ] Test extraction and running
- [ ] Verify all buttons work (multilingual)
- [ ] Check statistics display
- [ ] Test OTP sending

## Support & Updates

### Updating the Executable

1. Modify `FB_Recovery_Bot_Complete.py`
2. Run `BUILD_EXE.bat` again
3. Test new version
4. Increment version number
5. Redistribute

### Version Management

Update version in:
- `build_exe.py` (archive name)
- README.txt (version section)
- Executable properties (optional)

## FAQ

**Q: Why is the EXE so large?**
A: It includes Python runtime and all dependencies (80-120MB is normal).

**Q: Can I make it smaller?**
A: Yes, enable UPX compression and exclude unused modules.

**Q: Does it work on Windows 7?**
A: Officially supports Windows 10/11. Windows 7 may work but is not tested.

**Q: Why does antivirus flag it?**
A: PyInstaller executables are often false positives. Code signing helps.

**Q: Can I distribute commercially?**
A: Check licenses of included libraries (Selenium, CustomTkinter, etc).

**Q: How to update Chrome driver?**
A: The bot auto-downloads the latest driver via webdriver-manager.

---

**Version**: 1.0  
**Last Updated**: December 15, 2025  
**Build Tool**: PyInstaller 6.x  
**Python Version**: 3.8+
