import requests
import hashlib
import platform
import threading
import time
import json
import os
from pathlib import Path

# License Configuration
API_URL = "https://licencess.netlify.app/api/verifyLicense"
HEARTBEAT_URL = "https://licencess.netlify.app/api/heartbeat"
SERVER_API_KEY = "your_server_api_key_here"  # Replace with your API key
PRODUCT_ID = "prod_1"  # Replace with your product ID

# License storage file
LICENSE_FILE = Path.home() / ".fb_recovery_license"

def get_hardware_id():
    """Generate a unique hardware ID for this machine."""
    return hashlib.sha256(f"{platform.node()}-{platform.processor()}".encode()).hexdigest()

def verify_license(api_key, license_key, product_id, api_url):
    """Verify license and mark device as online."""
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
        response.raise_for_status()
        data = response.json()
        
        if data.get("valid"):
            print(f"✓ License verified! Online: {data.get('onlineDevices', 0)}/{data.get('maxDevices', 0)}")
            return True, data, data.get("heartbeatInterval", 180)
        else:
            print(f"✗ License invalid: {data.get('message')}")
            return False, data, None
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False, {"message": "Network error"}, None

def send_heartbeat(license_key, heartbeat_url):
    """Send heartbeat to maintain online status."""
    headers = {"Content-Type": "application/json"}
    payload = {"licenseKey": license_key, "hardwareId": get_hardware_id()}
    
    try:
        response = requests.post(heartbeat_url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print("💓 Heartbeat sent - device online")
    except:
        pass  # Silent fail - will retry in next interval

def heartbeat_loop(license_key, heartbeat_url, interval):
    """Background thread to send periodic heartbeats."""
    while True:
        time.sleep(interval)
        send_heartbeat(license_key, heartbeat_url)

def save_license(license_key):
    """Save license key to local file."""
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump({"license_key": license_key}, f)
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

def start_heartbeat(license_key, interval):
    """Start heartbeat thread to maintain online status."""
    if interval:
        threading.Thread(
            target=heartbeat_loop,
            args=(license_key, HEARTBEAT_URL, interval),
            daemon=True
        ).start()
        print(f"✓ Heartbeat started (every {interval}s)")
