# 🔐 License System Setup Guide

## Overview
The FB Recovery Bot now includes a license verification system that protects your application and tracks active devices.

## Configuration

### 1. Update License Manager Settings
Open `license_manager.py` and configure:

```python
# License Configuration
API_URL = "https://licencess.netlify.app/api/verifyLicense"
HEARTBEAT_URL = "https://licencess.netlify.app/api/heartbeat"
SERVER_API_KEY = "your_actual_api_key_here"  # ⚠️ REPLACE THIS
PRODUCT_ID = "prod_1"  # ⚠️ REPLACE WITH YOUR PRODUCT ID
```

### 2. Required Changes Before Distribution

#### In `license_manager.py`:
- Replace `SERVER_API_KEY` with your actual API key from your license panel
- Replace `PRODUCT_ID` with your product identifier

### 3. How It Works

**First Launch:**
1. User sees license activation window
2. Enters license key
3. System verifies with your license server
4. If valid, license is saved locally (optional)
5. Main application launches

**Subsequent Launches:**
1. System automatically checks saved license
2. Verifies in background (non-blocking)
3. If valid, main application opens immediately
4. If invalid, shows license window again

**During Runtime:**
- Heartbeat signals sent every 3 minutes (configurable)
- Maintains "online" status on your license server
- User appears as active device

### 4. Features

✅ **Automatic License Saving** - "Remember this license" option  
✅ **Background Verification** - Non-blocking saved license check  
✅ **Heartbeat System** - Maintains online device status  
✅ **Hardware ID Binding** - License tied to specific machine  
✅ **Beautiful UI** - Modern light theme matching main app  
✅ **Error Handling** - Network errors handled gracefully  

### 5. User Experience

**License Window Displays:**
- Clean, modern interface
- License key input field
- "Remember this license" checkbox
- Hardware ID display (for support)
- Clear status messages
- Activate and Exit buttons

**Status Messages:**
- 🔄 Verifying license...
- ✅ License verified! Starting application...
- ❌ License invalid: [error message]
- 💓 Heartbeat sent - device online (console)

### 6. Files Added

```
license_manager.py   - Core license verification logic
license_ui.py        - Beautiful CTk license window
```

### 7. Dependencies

Add to requirements or installation:
```bash
pip install requests
```

Already included: customtkinter, CTkMessagebox

### 8. License Storage

License saved to: `~/.fb_recovery_license` (hidden file in user's home directory)

Format:
```json
{"license_key": "user-license-key-here"}
```

### 9. Security Notes

⚠️ **Important:**
- Never commit your actual `SERVER_API_KEY` to public repositories
- Use environment variables for production
- Keep `LICENSE_FILE` location hidden
- The current implementation stores license in plaintext - consider encryption for production

### 10. Testing

**Test with invalid license:**
```python
# Run the bot
python FB_Recovery_Bot_Complete.py

# Enter any invalid key
# Should show: "❌ License invalid: [message]"
```

**Test with valid license:**
```python
# Enter your valid license key
# Should show: "✅ License verified!"
# Main app should launch
# Check console for heartbeat messages
```

**Test saved license:**
```python
# Close and reopen app
# Should auto-verify and open (if license was saved)
```

### 11. Customization

**Change heartbeat interval:**
The server returns `heartbeatInterval` (default 180 seconds). Modify server-side.

**Change window design:**
Edit `license_ui.py` - all UI customization is in `create_ui()` method.

**Change license storage location:**
Edit `LICENSE_FILE` in `license_manager.py`:
```python
LICENSE_FILE = Path.home() / ".your_custom_name"
```

### 12. Troubleshooting

**"License module not found" error:**
- Ensure `license_manager.py` and `license_ui.py` are in same directory as main bot
- Check file permissions

**Network errors:**
- Check internet connection
- Verify API URLs are correct
- Check firewall settings

**Invalid saved license:**
- License file is deleted automatically
- User will see activation window again

### 13. Production Checklist

Before releasing:
- [ ] Update `SERVER_API_KEY` with real API key
- [ ] Update `PRODUCT_ID` with your product ID
- [ ] Test with real license keys
- [ ] Test network failure scenarios
- [ ] Test saved license functionality
- [ ] Consider encrypting saved license
- [ ] Update main README with license info
- [ ] Add license purchase/support links

---

## Support

For license system issues, check:
1. Console output for detailed error messages
2. Network connectivity
3. API key configuration
4. License server status

---

**Created for FB Recovery Bot**  
License System Implementation - December 2025
