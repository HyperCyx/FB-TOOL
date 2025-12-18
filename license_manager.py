import requests
import hashlib
import platform
import json
import os
from pathlib import Path

# License Configuration
API_URL = "https://licencess.netlify.app/api/verifyLicense"
SERVER_API_KEY = "lg_server_8fd7679cfb1f4708a876e6fb1f70f9d5"
PRODUCT_ID = "prod_ea740f0d"

# License storage file
LICENSE_FILE = Path.home() / ".fb_recovery_license"

def get_hardware_id():
    """Generate a unique hardware ID for this machine."""
    return hashlib.sha256(f"{platform.node()}-{platform.processor()}".encode()).hexdigest()

def verify_license(api_key, license_key, product_id, api_url):
    """Verify license (one-time check, no heartbeat)."""
    # Anti-tamper check before verification
    try:
        from protection import verify_environment
        verify_environment()
    except ImportError:
        pass  # Protection not available
    except:
        # Silent exit on protection violation
        import os
        os._exit(1)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "licenseKey": license_key,
        "productId": product_id,
        "hardwareId": get_hardware_id()
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        # Try to parse JSON response regardless of status code
        try:
            data = response.json()
        except:
            # If JSON parsing fails, create error response
            return False, {
                "message": f"Server error: {response.status_code}",
                "error": "SERVER_ERROR"
            }
        
        # Check if license is valid
        if data.get("valid"):
            total_devices = data.get("totalDevices", data.get("activations", 0))
            max_devices = data.get("maxDevices", 0)
            print(f"✓ License verified!")
            print(f"✓ Total devices: {total_devices}/{max_devices}")
            return True, data
        else:
            # Extract error message and details
            error_msg = data.get("message", "Unknown error")
            error_code = data.get("error", "UNKNOWN")
            
            # Add more context based on error type
            if error_code == "LICENSE_EXPIRED":
                exp_date = data.get("expirationDate", "unknown")
                print(f"✗ License expired: {exp_date}")
            elif error_code == "DEVICE_LIMIT_REACHED" or "maximum devices" in error_msg.lower():
                max_dev = data.get("maxDevices", data.get("currentDevices", "unknown"))
                print(f"✗ Device limit reached: {max_dev} devices")
            else:
                print(f"✗ License invalid: {error_msg}")
            
            return False, data
            
    except requests.exceptions.Timeout:
        print(f"✗ Connection timeout")
        return False, {
            "message": "Connection timeout. Please check your internet connection.",
            "error": "TIMEOUT"
        }
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed")
        return False, {
            "message": "Unable to connect to license server. Please check your internet connection.",
            "error": "CONNECTION_ERROR"
        }
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False, {
            "message": f"Network error: {str(e)}",
            "error": "NETWORK_ERROR"
        }

def save_license(license_key):
    """Save license key to local file (hidden on all platforms)."""
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump({"license_key": license_key}, f)
        
        # Hide file on Windows
        if platform.system() == 'Windows':
            import ctypes
            # Set FILE_ATTRIBUTE_HIDDEN (0x02)
            ctypes.windll.kernel32.SetFileAttributesW(str(LICENSE_FILE), 0x02)
        
        return True
    except Exception as e:
        print(f"Error saving license: {e}")
        return False

def load_license():
    """Load license key from local file."""
    try:
        if LICENSE_FILE.exists():
            with open(LICENSE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("license_key")
    except Exception as e:
        print(f"Error loading license: {e}")
    return None

def delete_license():
    """Delete saved license file."""
    try:
        if LICENSE_FILE.exists():
            LICENSE_FILE.unlink()
        return True
    except Exception as e:
        print(f"Error deleting license: {e}")
        return False
