#!/usr/bin/env python3
"""
FB Recovery Bot - Windows EXE Builder
Builds a standalone executable for Windows distribution
"""

import os
import sys
import subprocess
import shutil

def check_requirements():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller found")
        return True
    except ImportError:
        print("❌ PyInstaller not found")
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")
        return True

def create_spec_file():
    """Create PyInstaller spec file for the bot"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['FB_Recovery_Bot_Complete.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'CTkMessagebox',
        'selenium',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'webdriver_manager',
        'webdriver_manager.chrome',
        'pyperclip',
        'pygetwindow',
        'requests',
        'psutil',
        'license_manager',
        'license_ui',
        'protection',
        'threading',
        'ctypes',
        'ctypes.wintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - will be in separate files for faster startup
    exclude_binaries=True,  # FASTER: Don't bundle everything in one file
    name='FB_Recovery_Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,  # No console window - GUI app with license system
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FB_Recovery_Bot',
)
'''
    
    with open('FB_Recovery_Bot.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ Created spec file: FB_Recovery_Bot.spec")

def build_exe():
    """Build the executable"""
    print("\n" + "="*60)
    print("🔨 BUILDING WINDOWS EXECUTABLE")
    print("="*60 + "\n")
    
    # Check requirements
    if not check_requirements():
        print("❌ Failed to install requirements")
        return False
    
    # Create spec file
    create_spec_file()
    
    # Clean previous builds
    if os.path.exists('build'):
        print("🧹 Cleaning build directory...")
        shutil.rmtree('build')
    if os.path.exists('dist'):
        print("🧹 Cleaning dist directory...")
        shutil.rmtree('dist')
    
    # Build using spec file
    print("\n🔨 Building executable (this may take several minutes)...\n")
    try:
        subprocess.check_call([
            sys.executable, 
            '-m', 
            'PyInstaller', 
            '--clean',
            '--noconfirm',
            'FB_Recovery_Bot.spec'
        ])
        
        print("\n" + "="*60)
        print("✅ BUILD SUCCESSFUL!")
        print("="*60)
        
        # Determine executable location (now in folder structure)
        import platform
        exe_folder = os.path.join('dist', 'FB_Recovery_Bot')
        exe_name = 'FB_Recovery_Bot.exe' if platform.system() == 'Windows' else 'FB_Recovery_Bot'
        exe_path = os.path.join(exe_folder, exe_name)
        
        if os.path.exists(exe_path):
            print(f"\n📦 Executable created: {exe_folder}/{exe_name}")
            print(f"📊 Executable size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
            
            # Calculate total folder size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(exe_folder):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            print(f"📊 Total package size: {total_size / (1024*1024):.2f} MB")
            print(f"⚡ FASTER STARTUP: Files are pre-extracted (no temp extraction)\n")
        else:
            print(f"\n⚠️  Executable name may differ on this platform")
            print(f"📁 Check dist/FB_Recovery_Bot/ folder for output\n")
        
        # Create distribution package
        create_distribution(exe_name)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False

def create_distribution(exe_name='FB_Recovery_Bot.exe'):
    """Create a distribution package with readme"""
    print("📦 Creating distribution package...")
    
    # Create dist folder structure
    dist_folder = 'FB_Recovery_Bot_Distribution'
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)
    
    # Copy entire executable folder (not just exe file)
    exe_folder = os.path.join('dist', 'FB_Recovery_Bot')
    if os.path.exists(exe_folder):
        print(f"   📂 Copying application folder...")
        shutil.copytree(exe_folder, os.path.join(dist_folder, 'FB_Recovery_Bot'))
    else:
        print(f"⚠️  Warning: {exe_folder} not found, skipping copy")
    
    # Create README for Windows users
    readme_content = """
# FB Recovery Bot - Windows Edition

## Quick Start

1. **Extract the entire folder** (don't move files separately)
2. Navigate to `FB_Recovery_Bot` folder
3. **Double-click** `FB_Recovery_Bot.exe` to launch the bot
4. Enter phone numbers (one per line)
5. Configure settings if needed
6. Click **START BOT**

**IMPORTANT**: Keep all files in the `FB_Recovery_Bot` folder together!
Don't move just the .exe file - it needs the other files to run.

## System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum
- Internet connection
- Google Chrome browser installed

## Features

✅ Modern Material Design UI
✅ Multi-threaded processing
✅ Embedded proxy support
✅ Real-time statistics
✅ Headless mode option
✅ Professional license system with online verification
✅ Advanced anti-debug protection
✅ Automatic license management
✅ Cross-platform compatible

## Proxy Configuration

To use a custom proxy:
1. Toggle "Custom Proxy Server" to ON
2. Enter proxy in format: `host:port:username:password`
3. Proxy will be saved for future sessions

## Live Statistics

- **Total Numbers**: Numbers in queue
- **OTP Sent**: Successfully sent SMS
- **No Account**: Numbers without Facebook accounts

## First Launch

On first launch, you'll see a license activation window:
1. Enter your license key
2. Click "Activate License"
3. License will be saved automatically
4. Bot will launch immediately after activation

## Troubleshooting

### Bot won't start
- Make sure Chrome is installed
- Run as Administrator if needed
- Check antivirus isn't blocking
- Close any debugger/developer tools

### License Issues
- Check internet connection for license verification
- Ensure license key is valid and not expired
- Contact support if device limit is reached

### Chrome not found
- Install Google Chrome from google.com/chrome
- Restart the bot after installation

### Proxy issues
- Verify proxy format: `host:port:user:pass`
- Check proxy is working in browser
- Try without proxy first

### Performance tips
- Use 2-3 concurrent instances for best results
- Enable headless mode for faster processing
- Close other Chrome instances before starting
- **Faster Startup**: This version uses folder structure (not single-file)
  for instant startup without temp extraction

## Support

For issues or questions, visit the GitHub repository.

## Version

All-In-One Edition with Embedded Proxy
Build Date: 2025

---
Developed with ❤️ using Python + CustomTkinter
"""
    
    with open(f'{dist_folder}/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Copy documentation if exists
    docs = ['QUICKSTART.md', 'PROXY_FEATURES.md', 'PROXY_FIXES.md', 'LICENSE_SETUP.md', 'PROTECTION_SYSTEM.md']
    for doc in docs:
        if os.path.exists(doc):
            try:
                shutil.copy(doc, dist_folder)
                print(f"   📄 Copied: {doc}")
            except:
                pass
    
    # Create ZIP archive
    import platform
    platform_name = platform.system()
    archive_name = f'{dist_folder}_v1.0_{platform_name}'
    print(f"🗜️  Creating ZIP archive: {archive_name}.zip")
    shutil.make_archive(archive_name, 'zip', dist_folder)
    
    print(f"\n✅ Distribution package created!")
    print(f"📁 Folder: {dist_folder}/")
    print(f"📦 Archive: {archive_name}.zip")
    print(f"🖥️  Platform: {platform_name}\n")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        FB RECOVERY BOT - EXE BUILDER                     ║
║        Windows Executable Creation Tool                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if not os.path.exists('FB_Recovery_Bot_Complete.py'):
        print("❌ Error: FB_Recovery_Bot_Complete.py not found!")
        print("Please run this script from the project directory.")
        sys.exit(1)
    
    success = build_exe()
    
    if success:
        print("\n🎉 All done! Your Windows executable is ready!")
        print("\n📋 Next steps:")
        print("   1. Test the executable: dist/FB_Recovery_Bot.exe")
        print("   2. Check the distribution folder: FB_Recovery_Bot_Windows/")
        print("   3. Share the ZIP file: FB_Recovery_Bot_Windows_v1.0.zip")
    else:
        print("\n❌ Build failed. Please check the errors above.")
        sys.exit(1)
