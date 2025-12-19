#!/usr/bin/env python3
# =====================================================
# 💙 FB RECOVERY BOT - ALL-IN-ONE EDITION
# By: YASHWIN KHAN | Admin: Hyper Red | Developer: HYPER RED
# Cross-Platform: Windows, Linux, Mac
# Auto Proxy Management with Embedded FLUXY
# License Protected with Online Verification
# =====================================================
# Installation:
# pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip requests

import os, threading, time, random, pyperclip, zipfile, tempfile, json
import socket, select, base64, sys, platform, subprocess
from queue import Queue
try:
    import pygetwindow as gw
    WINDOW_CONTROL_AVAILABLE = True
except:
    WINDOW_CONTROL_AVAILABLE = False
    
import customtkinter as ctk
from tkinter import messagebox
from CTkMessagebox import CTkMessagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG ==================
URL = "https://mbasic.facebook.com/login/identify/?ctx=recover&c=https://mbasic.facebook.com/&multiple_results=0&ars=facebook_login&from_login_screen=0&lwv=100&wtsid=rdr"
MAX_CONCURRENCY = 30
WINDOW_SIZE = (980, 720)
STAGGER = 40

# Embedded Proxy Configuration (User configurable from UI)
DEFAULT_PROXY = ""
LOCAL_PROXY_PORT = 8889

# Global proxy configuration (set from UI)
current_proxy_config = {
    'host': '',
    'port': 0,
    'user': '',
    'pass': ''
}
# ===========================================

success_numbers = []
running = False
bot_thread = None  # Track the main bot thread
bot_start_lock = threading.Lock()  # Prevent simultaneous starts
hidden_mode = False
browser_windows = []
local_proxy_thread = None
proxy_server_running = False

# Tab tracking system
active_tabs = {}  # {tab_id: {'driver': driver, 'number': number, 'last_activity': time, 'status': 'active/idle/working'}}
tab_counter = 0
tab_lock = threading.Lock()
stats_lock = threading.Lock()  # Thread-safe statistics updates
IDLE_TIMEOUT = 60  # Seconds of inactivity before considering tab idle
GLOBAL_IDLE_CHECK_INTERVAL = 5  # Check all tabs every 5 seconds

# Queue-based worker system
number_queue = Queue()  # Queue for phone numbers to process
worker_threads = []  # List of active worker threads
stats_updater_thread = None  # Real-time stats updater thread

# Number status tracking for activity log
number_status = {}  # {number: {'status': 'started/working/completed', 'result': 'otp_sent/no_account/failed', 'worker_id': int}}
number_status_lock = threading.Lock()

# =====================================================
# 🌐 EMBEDDED FLUXY PROXY (Auto-Start Integrated)
# =====================================================

def handle_proxy_client(client_socket, client_address, proxy_config):
    """Handle incoming client connection for proxy"""
    upstream = None
    try:
        request = b""
        client_socket.settimeout(5)
        while b"\r\n\r\n" not in request:
            chunk = client_socket.recv(4096)
            if not chunk:
                return
            request += chunk
            if len(request) > 65536:
                return
        
        request_line = request.split(b'\r\n')[0].decode('utf-8', errors='ignore')
        parts = request_line.split(' ')
        if len(parts) < 2:
            return
        
        method = parts[0]
        
        upstream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream.settimeout(10)
        upstream.connect((proxy_config['host'], proxy_config['port']))
        
        auth_string = f"{proxy_config['user']}:{proxy_config['pass']}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        auth_header = f"Proxy-Authorization: Basic {auth_bytes}\r\n"
        
        if method == "CONNECT":
            modified_request = request.replace(b'\r\n\r\n', f'\r\n{auth_header}\r\n'.encode())
            upstream.sendall(modified_request)
            
            response = upstream.recv(4096)
            client_socket.sendall(response)
            
            if b'200' in response or b'Connection established' in response.lower():
                client_socket.settimeout(60)
                upstream.settimeout(60)
                forward_proxy_tunnel(client_socket, upstream)
        else:
            modified_request = request.replace(b'\r\n\r\n', f'\r\n{auth_header}\r\n'.encode())
            upstream.sendall(modified_request)
            
            upstream.settimeout(30)
            while True:
                data = upstream.recv(8192)
                if not data:
                    break
                client_socket.sendall(data)
    
    except socket.timeout:
        pass
    except Exception as e:
        pass
    finally:
        try:
            client_socket.close()
        except:
            pass
        if upstream:
            try:
                upstream.close()
            except:
                pass

def forward_proxy_tunnel(client, server):
    """Bidirectional forwarding for HTTPS tunnel"""
    sockets = [client, server]
    
    while True:
        try:
            readable, _, exceptional = select.select(sockets, [], sockets, 60)
            
            if exceptional:
                break
            
            if not readable:
                break
            
            for sock in readable:
                try:
                    data = sock.recv(8192)
                    if not data:
                        return
                    
                    if sock is client:
                        server.sendall(data)
                    else:
                        client.sendall(data)
                except:
                    return
        except:
            break

def start_embedded_proxy_server(proxy_config):
    """Start the embedded proxy server in background thread with given config"""
    global proxy_server_running
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', LOCAL_PROXY_PORT))
        server.listen(100)
        
        proxy_server_running = True
        print(f"✅ Embedded proxy running on 127.0.0.1:{LOCAL_PROXY_PORT}", flush=True)
        print(f"🔄 Upstream: {proxy_config['host']}:{proxy_config['port']}", flush=True)
        
        while proxy_server_running:
            try:
                server.settimeout(1.0)  # Allow periodic checks
                try:
                    client_sock, addr = server.accept()
                    thread = threading.Thread(target=handle_proxy_client, args=(client_sock, addr, proxy_config))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue
            except Exception as e:
                if proxy_server_running:
                    continue
                else:
                    break
        
        server.close()
        print("🛑 Embedded proxy stopped", flush=True)
    except Exception as e:
        print(f"❌ Proxy server error: {e}", flush=True)
        proxy_server_running = False

def start_local_proxy(proxy_address=None):
    """Start embedded proxy in background thread with optional custom proxy"""
    global local_proxy_thread, proxy_server_running, current_proxy_config
    
    # Parse proxy address if provided
    if proxy_address:
        proxy_parts = [p.strip() for p in proxy_address.split(':')]
        if len(proxy_parts) >= 4:
            current_proxy_config = {
                'host': proxy_parts[0],
                'port': int(proxy_parts[1]),
                'user': proxy_parts[2],
                'pass': ':'.join(proxy_parts[3:])  # In case password contains ':'
            }
        else:
            print(f"⚠️ Invalid proxy format, using default", flush=True)
    
    # Check if already running
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', LOCAL_PROXY_PORT))
        sock.close()
        if result == 0:
            return True  # Already running
    except:
        pass
    
    # Start in thread with proxy config
    proxy_server_running = False
    local_proxy_thread = threading.Thread(target=start_embedded_proxy_server, args=(current_proxy_config,), daemon=True)
    local_proxy_thread.start()
    time.sleep(2)  # Give it time to start
    
    # Verify it started
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', LOCAL_PROXY_PORT))
        sock.close()
        return result == 0
    except:
        return False

def stop_local_proxy():
    """Stop the embedded proxy server"""
    global proxy_server_running, local_proxy_thread
    proxy_server_running = False
    
    # Wait for thread to finish
    if local_proxy_thread and local_proxy_thread.is_alive():
        local_proxy_thread.join(timeout=2)
    local_proxy_thread = None

def save_proxy_cache(proxy_address):
    """Save proxy to cache file"""
    cache_file = os.path.join(os.path.expanduser("~"), ".fb_bot_proxy_cache")
    try:
        with open(cache_file, 'w') as f:
            f.write(proxy_address)
        return True
    except Exception as e:
        print(f"Failed to save proxy cache: {e}")
        return False

def check_current_ip():
    """Check current IP address"""
    try:
        import urllib.request
        response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
        return response.read().decode('utf-8').strip()
    except:
        return "Unknown"

def check_proxy_ip():
    """Check IP through local proxy"""
    try:
        import urllib.request
        proxy_handler = urllib.request.ProxyHandler({'http': f'http://127.0.0.1:{LOCAL_PROXY_PORT}', 
                                                      'https': f'http://127.0.0.1:{LOCAL_PROXY_PORT}'})
        opener = urllib.request.build_opener(proxy_handler)
        response = opener.open('https://api.ipify.org', timeout=10)
        return response.read().decode('utf-8').strip()
    except Exception as e:
        return f"Error: {str(e)[:30]}"

# =====================================================
# 🤖 BOT CORE FUNCTIONS
# =====================================================

def human_type(element, text, min_delay=0.03, max_delay=0.1):
    """Paste number like a human using copy-paste behavior"""
    try:
        element.clear()
    except:
        pass
    
    # Small delay before pasting (human-like)
    time.sleep(random.uniform(0.2, 0.4))
    
    try:
        # Paste entire text at once (like Ctrl+V)
        element.send_keys(text)
    except:
        pass
    
    # Small delay after pasting (human-like)
    time.sleep(random.uniform(0.3, 0.5))

def find_input(driver):
    # Try mbasic Facebook specific input first
    try:
        input_el = driver.find_element(By.ID, 'identify_search_text_input')
        if input_el and input_el.is_displayed():
            return input_el
    except:
        pass
    
    # Try by name attribute
    try:
        input_el = driver.find_element(By.NAME, 'email')
        if input_el and input_el.is_displayed():
            return input_el
    except:
        pass
    
    # Try by data-sigil attribute
    try:
        input_el = driver.find_element(By.XPATH, '//input[@data-sigil="login_identify_search_placeholder"]')
        if input_el and input_el.is_displayed():
            return input_el
    except:
        pass
    
    # Fallback to generic method
    try:
        inputs = driver.find_elements(By.XPATH, '//input[@type="text" or @type="email" or @type="tel"]')
        if len(inputs) >= 2:
            return inputs[1]
        else:
            for el in inputs:
                if el.is_displayed():
                    return el
    except:
        pass
    return None

def find_search_button(driver):
    # Method 1: Try mbasic Facebook specific button by ID
    try:
        btn = driver.find_element(By.ID, 'did_submit')
        if btn and btn.is_displayed() and btn.is_enabled():
            return btn
    except:
        pass
    
    # Method 2: Try by name attribute
    try:
        btn = driver.find_element(By.NAME, 'did_submit')
        if btn and btn.is_displayed() and btn.is_enabled():
            return btn
    except:
        pass
    
    # Method 3: Try by data-sigil attribute
    try:
        btn = driver.find_element(By.XPATH, '//button[@data-sigil="touchable"][@type="submit"]')
        if btn and btn.is_displayed() and btn.is_enabled():
            return btn
    except:
        pass
    
    # Method 4: Multilingual button text support (fallback)
    texts = [
        "Search", "Continue", "Find", "Next", "Confirm",  # English
        "খুঁজুন", "চালিয়ে যান", "পরবর্তী", "নিশ্চিত করুন",  # Bengali
        "खोजें", "जारी रखें", "अगला", "पुष्टि करें",  # Hindi
        "بحث", "متابعة", "التالي", "تأكيد",  # Arabic
        "Buscar", "Continuar", "Siguiente", "Confirmar",  # Spanish
        "Rechercher", "Continuer", "Suivant", "Confirmer",  # French
        "Suchen", "Weiter", "Nächste", "Bestätigen",  # German
        "Pesquisar", "Continuar", "Próximo", "Confirmar",  # Portuguese
        "Cari", "Lanjutkan", "Berikutnya", "Konfirmasi",  # Indonesian
        "搜索", "继续", "下一步", "确认"  # Chinese
    ]
    
    for t in texts:
        try:
            el = driver.find_element(By.XPATH, f'//button[contains(text(),"{t}")]')
            if el.is_displayed() and el.is_enabled():
                return el
        except:
            pass
    
    # Method 5: Try any visible button with type="submit"
    try:
        buttons = driver.find_elements(By.XPATH, '//button[@type="submit"]')
        for btn in buttons:
            if btn.is_displayed() and btn.is_enabled():
                return btn
    except:
        pass
    
    # Method 6: Try any visible button in the form
    try:
        buttons = driver.find_elements(By.XPATH, '//form//button')
        for btn in buttons:
            if btn.is_displayed() and btn.is_enabled():
                return btn
    except:
        pass
    
    return None

def check_send_sms(driver):
    # Multilingual SMS option text
    sms_texts = [
        "SMS", "Send via SMS", "Text message",  # English
        "এসএমএস", "টেক্সট মেসেজ",  # Bengali
        "एसएमएस", "टेक्स्ट संदेश",  # Hindi
        "رسالة نصية",  # Arabic
        "Mensaje de texto",  # Spanish
        "Message texte",  # French
        "Textnachricht",  # German
        "Mensagem de texto",  # Portuguese
        "Pesan teks",  # Indonesian
        "短信"  # Chinese
    ]
    for text in sms_texts:
        try:
            el = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, f'//label[contains(., "{text}")]'))
            )
            if el.is_displayed():
                return el
        except:
            continue
    return None

def find_send_button(driver):
    # Priority Method 1: Detect by name="reset_action" (Continue button after SMS selection)
    try:
        el = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="reset_action"][data-sigil="touchable"]'))
        )
        if el.is_displayed() and el.is_enabled():
            return el
    except:
        pass
    
    # Priority Method 2: Detect by value="Continue"
    try:
        el = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[value="Continue"][data-sigil="touchable"]'))
        )
        if el.is_displayed() and el.is_enabled():
            return el
    except:
        pass
    
    # Fallback: Multilingual send/continue button text
    send_texts = [
        "Send", "Continue", "Confirm", "Submit",  # English
        "পাঠান", "চালিয়ে যান", "নিশ্চিত করুন",  # Bengali
        "भेजें", "जारी रखें", "पुष्टि करें",  # Hindi
        "إرسال", "متابعة", "تأكيد",  # Arabic
        "Enviar", "Continuar", "Confirmar",  # Spanish/Portuguese
        "Envoyer", "Continuer", "Confirmer",  # French
        "Senden", "Weiter", "Bestätigen",  # German
        "Kirim", "Lanjutkan", "Konfirmasi",  # Indonesian
        "发送", "继续", "确认"  # Chinese
    ]
    for text in send_texts:
        try:
            el = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[contains(., "{text}")]'))
            )
            if el.is_displayed():
                return el
        except:
            continue
    return None

def force_ui_refresh(widget):
    """Force immediate UI refresh for a widget"""
    try:
        widget.update_idletasks()
        widget.update()
    except:
        pass

def log_message(log_text, message):
    """Helper function to safely insert text into CTkTextbox with real-time updates"""
    try:
        log_text.configure(state="normal")
        log_text.insert("end", message)
        log_text.see("end")
        log_text.configure(state="disabled")
        # Force immediate UI update for real-time display
        log_text.update_idletasks()
        log_text.update()
        # Additional update for parent window to ensure visibility
        try:
            log_text.master.update_idletasks()
        except:
            pass
    except:
        pass

def update_number_status(number, status, result=None, worker_id=None):
    """Update the status of a number being processed"""
    global number_status
    with number_status_lock:
        if number not in number_status:
            number_status[number] = {}
        number_status[number]['status'] = status
        if result:
            number_status[number]['result'] = result
        if worker_id:
            number_status[number]['worker_id'] = worker_id

def get_number_status_display(number):
    """Get display string for number status"""
    with number_status_lock:
        if number not in number_status:
            return "❓ Unknown"
        
        status_info = number_status[number]
        status = status_info.get('status', 'unknown')
        result = status_info.get('result', None)
        worker_id = status_info.get('worker_id', '?')
        
        if status == 'started':
            return f"� STARTED → Worker #{worker_id}"
        elif status == 'working':
            return f"⚙️  PROCESSING → Worker #{worker_id}"
        elif status == 'completed':
            if result == 'otp_sent':
                return f"✅ SUCCESS → OTP Sent (Worker #{worker_id})"
            elif result == 'no_account':
                return f"❌ FAILED → No Account Found (Worker #{worker_id})"
            elif result == 'failed':
                return f"⚠️  FAILED → Error Occurred (Worker #{worker_id})"
            else:
                return f"✅ COMPLETED → Worker #{worker_id}"
        else:
            return f"❓ {status.title()} (Worker #{worker_id})"

def log_number_status(log_text, number, status, result=None, worker_id=None):
    """Log number status with formatted display"""
    update_number_status(number, status, result, worker_id)
    status_display = get_number_status_display(number)
    
    # Format with clearer display and immediate updates
    if status == 'started':
        log_message(log_text, f"\n{'─' * 50}\n")
        log_message(log_text, f"📱 Number: {number}\n")
        log_message(log_text, f"   {status_display}\n")
    elif status == 'completed':
        log_message(log_text, f"   {status_display}\n")
        log_message(log_text, f"{'─' * 50}\n")
    else:
        log_message(log_text, f"   {status_display}\n")
    
    # Force immediate refresh after every status update
    try:
        log_text.update_idletasks()
        log_text.update()
    except:
        pass

def register_tab(driver, number):
    """Register a new tab and return its unique ID"""
    global tab_counter, active_tabs
    with tab_lock:
        tab_counter += 1
        tab_id = tab_counter
        active_tabs[tab_id] = {
            'driver': driver,
            'number': number,
            'last_activity': time.time(),
            'status': 'working',
            'start_time': time.time()
        }
    return tab_id

def update_tab_activity(tab_id, status='working'):
    """Update tab's last activity time and status"""
    global active_tabs
    with tab_lock:
        if tab_id in active_tabs:
            active_tabs[tab_id]['last_activity'] = time.time()
            active_tabs[tab_id]['status'] = status

def unregister_tab(tab_id):
    """Remove tab from tracking"""
    global active_tabs
    with tab_lock:
        if tab_id in active_tabs:
            del active_tabs[tab_id]

def get_tab_info():
    """Get current tab statistics"""
    with tab_lock:
        total = len(active_tabs)
        working = sum(1 for t in active_tabs.values() if t['status'] == 'working')
        idle = sum(1 for t in active_tabs.values() if t['status'] == 'idle')
        return total, working, idle

def check_and_close_idle_tabs(log_text):
    """Check all tabs for idle timeout and close them"""
    global active_tabs, running
    current_time = time.time()
    tabs_to_close = []
    
    with tab_lock:
        for tab_id, tab_info in list(active_tabs.items()):
            total_lifetime = current_time - tab_info['start_time']
            idle_time = current_time - tab_info['last_activity']
            
            # Close tab if:
            # 1. Total lifetime exceeds 60 seconds (regardless of status)
            # 2. OR tab is idle/stopped for more than IDLE_TIMEOUT seconds
            if total_lifetime > 60:
                tabs_to_close.append((tab_id, tab_info, total_lifetime, 'lifetime'))
            elif tab_info['status'] != 'working' and idle_time > IDLE_TIMEOUT:
                tabs_to_close.append((tab_id, tab_info, idle_time, 'idle'))
    
    # Close tabs
    for tab_id, tab_info, duration, reason in tabs_to_close:
        try:
            if reason == 'lifetime':
                log_message(log_text, f"🆔 Tab #{tab_id} ({tab_info['number']}): ⏱️ Lifetime exceeded ({int(duration)}s) - force closing\n")
            else:
                log_message(log_text, f"🆔 Tab #{tab_id} ({tab_info['number']}): ⏱️ Idle for {int(duration)}s - closing\n")
            tab_info['driver'].quit()
            unregister_tab(tab_id)
        except:
            pass
    
    return len(tabs_to_close)

def close_all_idle_tabs(log_text):
    """Close all tabs that are not actively working"""
    global active_tabs
    closed_count = 0
    
    with tab_lock:
        tabs_to_close = [(tid, info) for tid, info in list(active_tabs.items()) if info['status'] != 'working']
    
    for tab_id, tab_info in tabs_to_close:
        try:
            log_message(log_text, f"🆔 Tab #{tab_id} ({tab_info['number']}): 🛑 Closing idle/stuck tab\n")
            tab_info['driver'].quit()
            unregister_tab(tab_id)
            closed_count += 1
        except:
            pass
    
    return closed_count

def handle_window(driver, number, log_text, stats, using_proxy=False):
    global running
    
    # Register this tab and get unique ID
    tab_id = register_tab(driver, number)
    log_message(log_text, f"🆔 Tab #{tab_id} created for {number}\n")
    
    # Maximum execution time for entire operation (reduced for large batches)
    MAX_EXECUTION_TIME = 90  # 1.5 minutes per number for efficiency
    start_time = time.time()
    
    def update_activity(status='working'):
        """Update this tab's activity"""
        update_tab_activity(tab_id, status)
    
    def check_timeout(operation_name=""):
        """Check if maximum execution time exceeded"""
        elapsed = time.time() - start_time
        if elapsed > MAX_EXECUTION_TIME:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⏱️ Timeout after {int(elapsed)}s at {operation_name} - closing tab\n")
            update_activity('stopped')
            with stats_lock:
                stats["checked"] += 1
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return True
        return False
    
    try:
        update_activity('working')
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Aborted before start\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            with stats_lock:
                stats["checked"] += 1
            return
        
        # Increase timeouts for proxy connections (shorter for large batches)
        if using_proxy:
            driver.set_page_load_timeout(45)  # Reduced for efficiency
            driver.implicitly_wait(10)
        else:
            driver.set_page_load_timeout(25)  # Reduced for efficiency
            driver.implicitly_wait(8)
        
        # Skip proxy test - go directly to Facebook
        if using_proxy:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🌐 Using proxy - loading Facebook directly...\n")
            update_activity('working')
        
        # Check timeout before loading Facebook
        if check_timeout("Facebook page load start"):
            stats["checked"] += 1
            return
        
        update_activity('working')
        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔵 Loading Facebook recovery page...\n")
        
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped before loading\n")
            update_activity('stopped')
            with stats_lock:
                stats["checked"] += 1
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return
        
        # Load Facebook with retry on timeout (reduced retries for large batches)
        max_retries = 1  # Only 1 retry for efficiency with large batches
        for retry in range(max_retries + 1):
            # Check stop status before each attempt
            if not running:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped during retry\n")
                with stats_lock:
                    stats["checked"] += 1
                return
            
            try:
                driver.get(URL)
                time.sleep(random.uniform(0.3, 0.7))  # Reduced wait
                update_activity('working')
                break
            except Exception as e:
                if retry < max_retries:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Timeout, retry {retry+1}...\n")
                    time.sleep(1)  # Shorter retry wait
                else:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ Load failed: {str(e)[:40]}\n")
                    update_activity('idle')
                    with stats_lock:
                        stats["checked"] += 1
                    return
            
            # Check timeout between retries
            if check_timeout(f"Facebook load retry {retry+1}"):
                with stats_lock:
                    stats["checked"] += 1
                return
        
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped during load\n")
            update_activity('stopped')
            with stats_lock:
                stats["checked"] += 1
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return

        # Check timeout before finding input
        if check_timeout("finding input box"):
            with stats_lock:
                stats["checked"] += 1
            return

        # Check if stopped before input search
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped before input search\n")
            with stats_lock:
                stats["checked"] += 1
            return
        
        update_activity('working')
        # Wait for input to be ready using WebDriverWait (reduced timeout for large batches)
        try:
            input_el = WebDriverWait(driver, 8).until(
                lambda d: find_input(d)
            )
        except:
            input_el = find_input(driver)
        
        if not input_el:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ Input box not found - closing tab\n")
            update_activity('stopped')
            with stats_lock:
                stats["checked"] += 1
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return

        # Check if stopped before entering number
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped before entering number\n")
            with stats_lock:
                stats["checked"] += 1
            return

        input_el.click()
        time.sleep(0.1)
        human_type(input_el, number)
        update_activity('working')
        time.sleep(0.2)

        # Check timeout before clicking search
        if check_timeout("clicking search button"):
            with stats_lock:
                stats["checked"] += 1
            return

        update_activity('working')
        btn = find_search_button(driver)
        if btn:
            try:
                # Try normal click first
                btn.click()
            except:
                try:
                    # Fallback to JavaScript click
                    driver.execute_script("arguments[0].click();", btn)
                except:
                    # Last resort: press Enter
                    input_el.send_keys(Keys.ENTER)
        else:
            # No button found, press Enter
            input_el.send_keys(Keys.ENTER)

        # Wait for page to load after search
        time.sleep(1.5)
        update_activity('working')

        # Check timeout after search
        if check_timeout("after search click"):
            with stats_lock:
                stats["checked"] += 1
            return

        # PRIORITY CHECK: Immediately check for "no account" message AFTER search
        try:
            page_text = driver.page_source.lower()
            
            # Check for "doesn't match an account" message first
            no_account_messages = [
                "doesn't match an account",
                "doesn't match any account", 
                "does not match an account",
                "does not match any account",
                "try again or create an account",
                "please try again or create",
                "no account found",
                "couldn't find your account",
                "can't find your account",
                "no search results",
                "no results found"
            ]
            
            for msg in no_account_messages:
                if msg in page_text:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ No account: '{msg}' detected - closing tab immediately\n")
                    log_number_status(log_text, number, 'completed', result='no_account', worker_id=tab_id)
                    update_activity('stopped')
                    with stats_lock:
                        stats["checked"] += 1
                        stats["no_account"] += 1
                    try:
                        driver.quit()
                        unregister_tab(tab_id)
                    except:
                        pass
                    return
        except Exception as e:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Could not check no-account message: {str(e)[:40]}\n")

        # PRIORITY: Check for "Sorry, something went wrong" error page - CLOSE IMMEDIATELY
        try:
            page_source = driver.page_source.lower()
            
            error_indicators = [
                "sorry, something went wrong",
                "something went wrong",
                "sorry something went wrong",
                "দুঃখিত, কিছু ভুল হয়েছে"  # Bengali: Sorry, something went wrong
            ]
            
            if any(error in page_source for error in error_indicators):
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ 'Something went wrong' error detected - closing tab immediately\n")
                log_number_status(log_text, number, 'completed', result='failed', worker_id=tab_id)
                update_activity('stopped')
                with stats_lock:
                    stats["checked"] += 1
                try:
                    driver.quit()
                    unregister_tab(tab_id)
                except:
                    pass
                return
        except:
            pass
        
        # Check for WhatsApp/Password alternative pages and handle "Try another way"
        alternative_page_detected = False
        page_type = None
        
        try:
            page_source = driver.page_source.lower()
            
            # Method 1: Check for WhatsApp login code page
            try:
                whatsapp_message = driver.find_element(By.ID, 'account_recovery_initiate_view_label')
                message_text = whatsapp_message.text.lower()
                if 'whatsapp' in message_text and ('login code' in message_text or 'send you' in message_text):
                    alternative_page_detected = True
                    page_type = "WhatsApp"
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✓ WhatsApp login page detected\n")
            except:
                pass
            
            # Method 2: Check for password entry page
            if not alternative_page_detected:
                try:
                    # Check for password-related text
                    password_indicators = [
                        ('password' in page_source and 'try another way' in page_source),
                        ('enter your password' in page_source and 'try another way' in page_source),
                        ('পাসওয়ার্ড' in page_source and 'try another way' in page_source)  # Bengali password
                    ]
                    
                    if any(password_indicators):
                        alternative_page_detected = True
                        page_type = "Password"
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✓ Password entry page detected\n")
                except:
                    pass
            
            # Method 3: Generic alternative method detection
            if not alternative_page_detected:
                try:
                    # Look for any page with "try another way" that's not SMS page
                    if 'try another way' in page_source:
                        # Make sure it's not already on SMS page
                        if 'sms' not in page_source or 'text message' not in page_source:
                            alternative_page_detected = True
                            page_type = "Alternative"
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✓ Alternative recovery page detected\n")
                except:
                    pass
        except:
            pass
        
        # Only proceed with bypass if alternative page detected
        if alternative_page_detected:
            try:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ {page_type} recovery page - bypassing...\n")
                update_activity('working')
                time.sleep(0.2)
                
                # Multiple methods to find "Try another way" button/link
                button_found = False
                
                # Method 1: Use WebDriverWait for instant "try another way" button detection
                try:
                    try_another_elem = WebDriverWait(driver, 3).until(
                        lambda d: next(
                            (elem for elem in d.find_elements(By.XPATH, "//*[contains(translate(text(), 'TRY ANOTHER WAY', 'try another way'), 'try another way')]") 
                             if elem.is_displayed()), 
                            None
                        )
                    )
                    if try_another_elem:
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔍 Found 'Try another way' - clicking instantly...\n")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", try_another_elem)
                        driver.execute_script("arguments[0].click();", try_another_elem)
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Clicked 'Try another way'\n")
                        button_found = True
                        time.sleep(0.3)
                except Exception as e:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Method 1 timeout: {str(e)[:30]}\n")
                
                # Method 2: Look for links/buttons with specific text
                if not button_found:
                    try_another_way_texts = ["Try another way", "try another way", "TRY ANOTHER WAY", "অন্যভাবে চেষ্টা করুন"]
                    for text in try_another_way_texts:
                        try:
                            try_another_btn = driver.find_element(By.XPATH, f"//a[contains(., '{text}')] | //button[contains(., '{text}')] | //span[contains(., '{text}')]")
                            if try_another_btn and try_another_btn.is_displayed():
                                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔍 Found button with text '{text}'\n")
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", try_another_btn)
                                driver.execute_script("arguments[0].click();", try_another_btn)
                                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Clicked 'Try another way'\n")
                                button_found = True
                                time.sleep(0.3)
                                break
                        except:
                            continue
                
                # Method 3: Look for any clickable element with "another" in text
                if not button_found:
                    try:
                        all_clickable = driver.find_elements(By.XPATH, "//a | //button | //span[@role='button']")
                        for elem in all_clickable:
                            try:
                                elem_text = elem.text.lower()
                                if 'another' in elem_text and 'way' in elem_text:
                                    if elem.is_displayed():
                                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔍 Found alternative element - clicking...\n")
                                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", elem)
                                        driver.execute_script("arguments[0].click();", elem)
                                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Clicked alternative button\n")
                                        button_found = True
                                        time.sleep(0.3)
                                        break
                            except:
                                continue
                    except:
                        pass
                
                if not button_found:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ Could not find 'Try another way' button\n")
                else:
                    # After clicking "Try another way", continue to next page
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Bypassed {page_type} page, continuing...\n")
                    time.sleep(0.3)
                    
                    # Check if another alternative page appears (nested recovery options)
                    try:
                        time.sleep(0.2)
                        nested_page_source = driver.page_source.lower()
                        
                        # If another "try another way" appears, click it again
                        if 'try another way' in nested_page_source:
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔄 Nested recovery page detected - clicking instantly...\n")
                            
                            # Use WebDriverWait for instant nested button detection
                            try:
                                nested_elem = WebDriverWait(driver, 2).until(
                                    lambda d: next(
                                        (elem for elem in d.find_elements(By.XPATH, "//*[contains(translate(text(), 'TRY ANOTHER WAY', 'try another way'), 'try another way')]") 
                                         if elem.is_displayed()), 
                                        None
                                    )
                                )
                            except:
                                nested_try_another = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'TRY ANOTHER WAY', 'try another way'), 'try another way')]")
                                nested_elem = next((elem for elem in nested_try_another if elem.is_displayed()), None)
                            
                            if nested_elem:
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", nested_elem)
                                driver.execute_script("arguments[0].click();", nested_elem)
                                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Clicked nested 'Try another way'\n")
                                time.sleep(0.2)
                    except:
                        pass
            except Exception as e:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Alternative page bypass error: {str(e)[:50]}\n")
        else:
            # No alternative page detected, skip this section
            pass

        # Check for "Choose Your Account" page (multiple accounts found)
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped after search\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return
        
        # Quick check if multiple accounts page appears (only sometimes)
        account_selection_detected = False
        try:
            # Fast detection - check page source once
            page_text = driver.page_source.lower()
            
            # Multiple account indicators
            account_selection_indicators = [
                "choose your account",
                "choose an account",
                "select your account",
                "select an account",
                "which account",
                "multiple accounts",
                "একটি অ্যাকাউন্ট বেছে নিন",  # Bengali: Choose an account
                "আপনার অ্যাকাউন্ট বেছে নিন"  # Bengali: Choose your account
            ]
            
            # Quick check - only proceeds if detected
            account_selection_detected = any(indicator in page_text for indicator in account_selection_indicators)
            
            if not account_selection_detected:
                # Account selection page NOT present - continue normally
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ℹ️  Single account - no selection needed\n")
        except:
            pass
        
        # Only handle account selection if page is detected
        if account_selection_detected:
            try:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ℹ️  Multiple accounts found - clicking FIRST account FAST...\n")
                update_activity('working')
                time.sleep(0.15)  # Reduced wait
                
                account_selected = False
                first_clickable = None
                
                # FASTEST METHOD: Target exact "Choose Your Account" page structure
                # Priority 1: Find account items with specific class structure (from inspection)
                account_items = driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'item') and contains(@class, '_7br9') and @data-sigil='marea']//a[contains(@class, 'touchable') and contains(@class, 'primary')]")
                
                if account_items and len(account_items) > 0:
                    # Click FIRST account link
                    first_clickable = account_items[0]
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚡ Found {len(account_items)} accounts - clicking FIRST...\n")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", first_clickable)
                    driver.execute_script("arguments[0].click();", first_clickable)
                    account_selected = True
                    time.sleep(0.3)
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ FIRST account clicked successfully\n")
                else:
                    # Fallback: Broader search for all possible account elements
                    all_elements = driver.find_elements(By.XPATH, 
                            "//div[@data-sigil='marea']//a[contains(@class, 'touchable')] | "
                            "//a[contains(@class, 'touchable') and contains(@class, 'primary')] | "
                            "//label[contains(@class, 'recover')] | "
                            "//label[@data-sigil='touchable'] | "
                            "//label[contains(@for, 'radio')] | "
                            "//input[@type='radio'] | "
                            "//input[@type='checkbox'] | "
                            "//table//tr[@data-sigil='touchable'] | "
                            "//table//tr[.//input[@type='radio']] | "
                            "//div[@data-sigil='touchable'] | "
                        "//form//label[1] | "
                        "//form//tr[1]")
                    
                    # Find FIRST visible element from all collected
                    for elem in all_elements:
                        try:
                            if elem.is_displayed():
                                first_clickable = elem
                                break  # STOP at first visible
                        except:
                            continue
                    
                    if first_clickable:
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚡ FALLBACK - clicking FIRST account element...\n")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", first_clickable)
                        driver.execute_script("arguments[0].click();", first_clickable)
                        account_selected = True
                        time.sleep(0.3)
                        
                        # If it was a radio button, also click its label
                        if first_clickable.tag_name == 'input':
                            try:
                                elem_id = first_clickable.get_attribute('id')
                                if elem_id:
                                    label = driver.find_element(By.XPATH, f"//label[@for='{elem_id}']")
                                    driver.execute_script("arguments[0].click();", label)
                            except:
                                pass
                
                # Fallback: Try clicking first visible element in page (last resort)
                if not account_selected:
                    try:
                        # Get first clickable thing on page
                        any_clickable = driver.find_elements(By.XPATH, "//a | //button | //label | //div[@role='button']")
                        for elem in any_clickable[:10]:  # Check first 10 only
                            try:
                                if elem.is_displayed() and 'account' in elem.text.lower():
                                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔘 Fallback click on account element...\n")
                                    driver.execute_script("arguments[0].click();", elem)
                                    account_selected = True
                                    time.sleep(0.3)
                                    break
                            except:
                                continue
                    except Exception as e:
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Fallback failed: {str(e)[:30]}\n")
                
                if account_selected:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Account selected from multiple options\n")
                    time.sleep(0.4)  # Quick wait for page to load after account selection
                    
                    # After account selection, there might be a "Continue" or "Next" button
                    try:
                        # Look for Continue/Next button
                        continue_btn = find_send_button(driver)
                        if continue_btn:
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔹 Clicking Continue/Next button...\n")
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", continue_btn)
                            time.sleep(0.1)
                            driver.execute_script("arguments[0].click();", continue_btn)
                            time.sleep(0.6)
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Proceeding to recovery options...\n")
                        else:
                            # No button found, account click might have auto-submitted
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ℹ️  No Continue button needed, auto-proceeding...\n")
                            time.sleep(0.3)
                    except Exception as e:
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Continue button error: {str(e)[:30]}\n")
                    else:
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Could not auto-select account (5 methods tried)\n")
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ℹ️  Continuing anyway - may need manual selection...\n")
            except Exception as e:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Account selection check error: {str(e)[:50]}\n")
        
        # Skip early error check - we'll check AFTER SMS send attempt
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped after account selection\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return
        
        # Check for "No search result" or similar messages
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped after error check\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return
        
        try:
            # Secondary check for "no result" messages (backup check)
            no_result_indicators = [
                "couldn't find",
                "can't find",
                "no matches",
                "পাওয়া যায়নি",  # Bengali: Not found
                "ফলাফল নেই"  # Bengali: No result
            ]
            
            page_text = driver.page_source.lower()
            
            for indicator in no_result_indicators:
                if indicator in page_text:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ No account (secondary check): '{indicator}' - closing tab\n")
                    log_number_status(log_text, number, 'completed', result='no_account', worker_id=tab_id)
                    update_activity('stopped')
                    with stats_lock:
                        stats["checked"] += 1
                        stats["no_account"] += 1
                    try:
                        driver.quit()
                        unregister_tab(tab_id)
                    except:
                        pass
                    return
        except Exception as e:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Could not check for no-result: {str(e)[:40]}\n")

        # Check timeout before SMS check
        if check_timeout("SMS option check"):
            with stats_lock:
                stats["checked"] += 1
            return
        
        # Check if stopped
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped before SMS check\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return

        update_activity('working')
        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔍 Looking for SMS/Text recovery option...\n")
        
        # Enhanced SMS option detection
        sms_option = None
        try:
            # Method 1: Use existing check_send_sms function with wait
            sms_option = WebDriverWait(driver, 5).until(
                lambda d: check_send_sms(d)
            )
        except:
            pass
        
        # Method 2: Direct search for SMS-related elements if method 1 fails
        if not sms_option:
            try:
                sms_elements = driver.find_elements(By.XPATH,
                    "//label[contains(translate(., 'SMS', 'sms'), 'sms')] | "
                    "//label[contains(translate(., 'TEXT', 'text'), 'text message')] | "
                    "//input[@type='radio'][contains(@id, 'sms')] | "
                    "//input[@type='radio'][contains(@value, 'sms')] | "
                    "//label[contains(., 'Send code via SMS')] | "
                    "//label[contains(., 'Text message')] | "
                    "//div[contains(., 'SMS') and @data-sigil='touchable']")
                for elem in sms_elements:
                    if elem.is_displayed():
                        sms_option = elem
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✓ Found SMS option (direct search)\n")
                        break
            except:
                pass
        
        if sms_option:
            # Scroll SMS option into view and click immediately
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", sms_option)
                time.sleep(0.1)
                driver.execute_script("arguments[0].click();", sms_option)
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ SMS option clicked successfully\n")
                update_activity('working')
                time.sleep(0.3)  # Wait for SMS option to be selected
            except Exception as e:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ SMS click error: {str(e)[:40]}\n")

            # Check timeout before send button
            if check_timeout("finding send button"):
                with stats_lock:
                    stats["checked"] += 1
                return

            update_activity('working')
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔍 Looking for Send/Continue button...\n")
            
            # Enhanced send button detection
            send_btn = None
            try:
                send_btn = WebDriverWait(driver, 5).until(
                    lambda d: find_send_button(d)
                )
            except:
                pass
            
            # Fallback: Direct button search
            if not send_btn:
                try:
                    buttons = driver.find_elements(By.XPATH,
                        "//button[@type='submit'] | "
                        "//button[@name='reset_action'] | "
                        "//button[@data-sigil='touchable'][@type='submit'] | "
                        "//button[contains(., 'Continue')] | "
                        "//button[contains(., 'Send')] | "
                        "//input[@type='submit']")
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            send_btn = btn
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✓ Found button (direct search)\n")
                            break
                except:
                    pass
            
            if send_btn:
                try:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 📤 Clicking Send/Continue button...\n")
                    # Scroll and click
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", send_btn)
                    time.sleep(0.1)
                    driver.execute_script("arguments[0].click();", send_btn)
                    update_activity('working')
                    time.sleep(1)  # Wait for SMS to be sent
                    
                    # Verify SMS was sent by checking page content
                    try:
                        page_text = driver.page_source.lower()
                        success_indicators = [
                            "code sent",
                            "sent to",
                            "check your",
                            "enter the code",
                            "enter code",
                            "confirmation code",
                            "we sent",
                            "we've sent"
                        ]
                        
                        sms_sent_confirmed = any(indicator in page_text for indicator in success_indicators)
                        
                        if sms_sent_confirmed:
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ SMS sent VERIFIED (code page detected)\n")
                        else:
                            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ SMS sent (assuming success)\n")
                    except:
                        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ SMS sent\n")
                    
                    # No additional error check - assume success
                    success_numbers.append(number)
                    with stats_lock:
                        stats["otp_sent"] += 1
                    log_number_status(log_text, number, 'completed', result='otp_sent', worker_id=tab_id)
                    update_activity('working')
                        
                except Exception as e:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Send button click error: {str(e)[:40]}\n")
                    with stats_lock:
                        stats["checked"] += 1
                    log_number_status(log_text, number, 'completed', result='failed', worker_id=tab_id)
            else:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠ SMS option found but no Send button - closing tab\n")
                log_number_status(log_text, number, 'completed', result='failed', worker_id=tab_id)
                update_activity('stopped')
                with stats_lock:
                    stats["checked"] += 1
                try:
                    driver.quit()
                    unregister_tab(tab_id)
                except:
                    pass
        else:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ No SMS option found - closing tab\n")
            log_number_status(log_text, number, 'completed', result='failed', worker_id=tab_id)
            update_activity('stopped')
            with stats_lock:
                stats["checked"] += 1
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass

    except Exception as e:
        log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ Error: {str(e)[:100]} - closing tab\n")
        log_number_status(log_text, number, 'completed', result='failed', worker_id=tab_id)
        update_activity('stopped')
        with stats_lock:
            stats["checked"] += 1
        try:
            driver.quit()
            unregister_tab(tab_id)
        except:
            pass
        return
    finally:
        # ALWAYS close the browser tab when done (success, error, or timeout)
        total_time = time.time() - start_time
        
        # Determine reason for closure
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped by user - closing tab\n")
            update_activity('stopped')
        elif number in success_numbers:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ Success - closing tab after {int(total_time)}s\n")
            update_activity('working')
        elif total_time > MAX_EXECUTION_TIME:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⏱️ Timeout after {int(total_time)}s - closing tab\n")
            update_activity('stopped')
            if number not in success_numbers:
                with stats_lock:
                    stats["checked"] += 1
        else:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Error occurred - closing tab\n")
            update_activity('stopped')
        
        # ALWAYS close browser and unregister tab (no conditions)
        try:
            driver.quit()
        except Exception as e:
            # Log quit error but continue
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Browser close error: {str(e)[:30]}\n")
        finally:
            # Always unregister tab even if quit fails
            unregister_tab(tab_id)

def open_browser_instance(index, number, log_text, stats, proxy_config=None):
    using_proxy = False
    
    opts = ChromeOptions()
    opts.add_argument(f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    # Tablet User Agent (iPad)
    opts.add_argument("user-agent=Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")
    
    if proxy_config and proxy_config.get('enabled'):
        log_message(log_text, f"{number}: 🌐 Using embedded proxy (localhost:{LOCAL_PROXY_PORT})\n")
        opts.add_argument(f"--proxy-server=http://127.0.0.1:{LOCAL_PROXY_PORT}")
        # Ignore SSL certificate errors when using proxy
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument("--ignore-ssl-errors")
        # Increase timeout settings for proxy
        opts.add_argument("--dns-prefetch-disable")
        using_proxy = True
    else:
        log_message(log_text, f"{number}: ℹ️  Direct connection\n")
    
    if hidden_mode:
        opts.add_argument("--headless")
    
    try:
        # Check if still running before creating expensive browser
        if not running:
            log_message(log_text, f"{number}: 🛑 Stopped before Chrome start\n")
            with stats_lock:
                stats["checked"] += 1
            return
        
        log_message(log_text, f"{number}: 🚀 Starting Chrome...\n")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
        
        # Check again after browser creation (slow operation)
        if not running:
            log_message(log_text, f"{number}: 🛑 Stopped during Chrome start\n")
            try:
                driver.quit()
            except:
                pass
            with stats_lock:
                stats["checked"] += 1
            return
        
        browser_windows.append(driver)
        driver.set_window_position(index * STAGGER, index * STAGGER)
        log_message(log_text, f"{number}: ✅ Chrome started\n")
            
    except Exception as e:
        log_message(log_text, f"{number}: ❌ Chrome failed: {str(e)[:100]}\n")
        with stats_lock:
            stats["checked"] += 1
        return
    
    if hidden_mode and WINDOW_CONTROL_AVAILABLE:
        try:
            time.sleep(0.5)
            for w in gw.getWindowsWithTitle("Chrome"):
                w.minimize()
        except:
            pass
    
    handle_window(driver, number, log_text, stats, using_proxy)

def global_idle_checker(log_text, stats_labels):
    """Background thread that checks and closes idle tabs every 10 seconds"""
    while running:
        try:
            time.sleep(GLOBAL_IDLE_CHECK_INTERVAL)
            if not running:
                break
            
            # Check and close idle tabs
            closed_count = check_and_close_idle_tabs(log_text)
            if closed_count > 0:
                log_message(log_text, f"🧹 Global checker closed {closed_count} idle tabs\n")
            
            # Update tab statistics
            total_tabs, working_tabs, idle_tabs = get_tab_info()
            if stats_labels and "active_tabs" in stats_labels:
                stats_labels["active_tabs"].configure(text=f"{total_tabs} ({working_tabs}W/{idle_tabs}I)")
        except Exception as e:
            # Silently continue on errors
            pass

def queue_worker(worker_id, log_text, stats, proxy_config):
    """Worker thread that continuously pulls numbers from queue and processes them"""
    global running
    
    log_message(log_text, f"👷 Worker #{worker_id} started and waiting for numbers...\n")
    
    while running:
        try:
            # Get number from queue with timeout to check running status
            try:
                number = number_queue.get(timeout=1)
            except:
                # Queue empty or timeout, check if still running
                if not running:
                    break
                continue
            
            if number is None:  # Poison pill to stop worker
                number_queue.task_done()
                break
            
            # Log number started
            log_number_status(log_text, number, 'started', worker_id=worker_id)
            
            # Process the number
            log_number_status(log_text, number, 'working', worker_id=worker_id)
            open_browser_instance(worker_id, number, log_text, stats, proxy_config)
            
            # Note: final status will be updated by handle_window function
            
            # Mark task as done
            number_queue.task_done()
            
            # Small delay between processing
            time.sleep(0.3)
            
        except Exception as e:
            log_message(log_text, f"⚠️ Worker #{worker_id} error: {str(e)[:50]}\n")
            try:
                number_queue.task_done()
            except:
                pass
    
    log_message(log_text, f"👷 Worker #{worker_id} stopped.\n")

def realtime_stats_updater(stats, stats_labels, progress, total_numbers):
    """Background thread that updates GUI statistics in real-time"""
    global running
    
    while running:
        try:
            time.sleep(0.3)  # Faster updates - every 0.3 seconds for real-time feel
            
            if not running:
                break
            
            # Get current stats with lock
            with stats_lock:
                checked = stats["checked"]
                otp_sent = stats["otp_sent"]
                no_account = stats["no_account"]
            
            # Update GUI labels with forced refresh
            try:
                stats_labels["total"].configure(text=f"{total_numbers}")
                stats_labels["otp_sent"].configure(text=f"{otp_sent}")
                stats_labels["no_account"].configure(text=f"{no_account}")
                
                # Calculate remaining
                remaining = total_numbers - checked
                if "remaining" in stats_labels:
                    stats_labels["remaining"].configure(text=f"{remaining}")
                
                # Update progress bar
                progress_val = (checked / total_numbers) if total_numbers > 0 else 0
                progress.set(progress_val)
                
                # Update tab statistics
                total_tabs, working_tabs, idle_tabs = get_tab_info()
                if "active_tabs" in stats_labels:
                    stats_labels["active_tabs"].configure(text=f"{total_tabs} ({working_tabs}W/{idle_tabs}I)")
                
                # Force immediate UI update on all widgets
                for label in stats_labels.values():
                    label.update_idletasks()
                progress.update_idletasks()
                progress.update()
            except:
                pass  # Ignore UI update errors
            
        except Exception as e:
            pass  # Silently continue on errors

def run_bot(numbers, log_text, result_box, progress, stats_labels, concurrency_var, proxy_enabled_var=None, proxy_var=None, stop_btn=None, start_btn=None, ip_label=None):
    global running, number_status, bot_thread
    
    # Prevent multiple simultaneous starts
    with bot_start_lock:
        if running:
            log_message(log_text, "⚠️ Bot is already running!\n")
            return
        
        running = True
        success_numbers.clear()
    
    # Clear number status tracking
    with number_status_lock:
        number_status.clear()
    
    if stop_btn:
        stop_btn.configure(state="normal")
    if start_btn:
        start_btn.configure(state="disabled")
    
    # Start global idle checker thread
    idle_checker_thread = threading.Thread(target=global_idle_checker, args=(log_text, stats_labels), daemon=True)
    idle_checker_thread.start()
    log_message(log_text, f"🔍 Global tab monitor started (1-min timeout per tab, checks every {GLOBAL_IDLE_CHECK_INTERVAL}s)\n")
    
    proxy_enabled = proxy_enabled_var.get() if proxy_enabled_var else False
    proxy_address = proxy_var.get().strip() if proxy_var else None
    
    if proxy_enabled:
        # Save proxy to cache
        if proxy_address:
            save_proxy_cache(proxy_address)
        
        log_message(log_text, f"🌐 Proxy enabled - starting embedded proxy...\n")
        if proxy_address:
            log_message(log_text, f"🔧 Using custom proxy: {proxy_address.split(':')[0]}:{proxy_address.split(':')[1]}\n")
        if start_local_proxy(proxy_address):
            log_message(log_text, f"✅ Embedded proxy started automatically!\n")
            log_message(log_text, f"✅ No authentication popups needed!\n")
            
            # Wait for proxy to fully initialize
            log_message(log_text, f"⏳ Waiting for proxy to initialize (3 seconds)...\n")
            time.sleep(3)
            
            # Check and display proxy IP
            if ip_label:
                log_message(log_text, f"🔍 Checking proxy IP...\n")
                proxy_ip = check_proxy_ip()
                ip_label.configure(text=f"Current IP: {proxy_ip} (via proxy)", text_color="#00B894")
                log_message(log_text, f"✅ Proxy IP: {proxy_ip}\n")
        else:
            log_message(log_text, f"⚠️ Proxy failed to start\n")
            if ip_label:
                ip_label.configure(text="Current IP: Proxy failed", text_color="#FF7675")
    else:
        # Stop proxy if running
        stop_local_proxy()
        log_message(log_text, f"ℹ️  Proxy disabled - direct connection\n")
        
        # Check and display system IP
        if ip_label:
            log_message(log_text, f"🔍 Checking system IP...\n")
            system_ip = check_current_ip()
            ip_label.configure(text=f"Current IP: {system_ip} (direct)", text_color="#6C5CE7")
            log_message(log_text, f"✅ System IP: {system_ip}\n")
    
    log_message(log_text, f"\n{'═' * 50}\n")
    log_message(log_text, f"🚀 STARTING BOT\n")
    log_message(log_text, f"📊 Total Numbers: {len(numbers)}\n")

    total = len(numbers)
    stats = {"checked": 0, "otp_sent": 0, "no_account": 0}
    concurrency = min(int(concurrency_var.get()), MAX_CONCURRENCY)
    
    log_message(log_text, f"⚙️  Concurrent Workers: {concurrency}\n")
    log_message(log_text, f"{'═' * 50}\n\n")

    proxy_config = {'enabled': proxy_enabled} if proxy_enabled else None
    
    # ========== NEW QUEUE-BASED SYSTEM ==========
    global number_queue, worker_threads, stats_updater_thread
    
    # Clear queue and worker list completely
    log_message(log_text, f"🧹 Cleaning up previous session...\n")
    queue_cleared = 0
    while not number_queue.empty():
        try:
            number_queue.get_nowait()
            number_queue.task_done()
            queue_cleared += 1
        except:
            break
    
    if queue_cleared > 0:
        log_message(log_text, f"🗑️ Cleared {queue_cleared} items from previous session\n")
    
    # Wait for any remaining worker threads
    if worker_threads:
        log_message(log_text, f"⏳ Waiting for {len(worker_threads)} old workers to finish...\n")
        for worker in worker_threads:
            try:
                if worker.is_alive():
                    worker.join(timeout=2)
            except:
                pass
    
    worker_threads.clear()
    log_message(log_text, f"✅ Previous session cleanup complete\n")
    
    log_message(log_text, f"📊 Queue-based system starting...\n")
    log_message(log_text, f"👷 Creating {concurrency} worker threads...\n")
    
    # Add all numbers to queue
    valid_numbers = [num.strip() for num in numbers if num.strip() != ""]
    for number in valid_numbers:
        number_queue.put(number)
    
    log_message(log_text, f"✅ Added {len(valid_numbers)} numbers to queue\n")
    
    # Start real-time stats updater
    stats_updater_thread = threading.Thread(
        target=realtime_stats_updater, 
        args=(stats, stats_labels, progress, total), 
        daemon=True
    )
    stats_updater_thread.start()
    log_message(log_text, f"📈 Real-time stats updater started (updates every 0.5s)\n")
    
    # Start worker threads
    for worker_id in range(concurrency):
        worker = threading.Thread(
            target=queue_worker,
            args=(worker_id + 1, log_text, stats, proxy_config),
            daemon=False
        )
        worker.start()
        worker_threads.append(worker)
        # Stagger worker starts slightly
        time.sleep(0.3 if not proxy_config or not proxy_config.get('enabled') else 1.0)
    
    log_message(log_text, f"✅ {concurrency} workers started and processing...\n")
    log_message(log_text, f"⚡ Workers will automatically pull numbers from queue!\n")
    log_message(log_text, f"⚡ As soon as one finishes, it takes the next number!\n")
    
    # Wait for queue to be empty (all numbers processed) - but exit immediately if stopped
    log_message(log_text, f"⏳ Waiting for all numbers to be processed...\n")
    
    # Monitor queue completion with running flag check
    while running and not number_queue.empty():
        try:
            # Check every 0.5 seconds if we should stop
            time.sleep(0.5)
        except:
            break
    
    # If stopped early, skip waiting for queue.join()
    if running:
        # Normal completion - wait for queue
        try:
            number_queue.join()
        except:
            pass
    else:
        # Stopped by user - exit immediately
        log_message(log_text, f"🛑 Stopped by user - exiting immediately\n")
    
    # Send poison pills to stop workers
    if running:
        log_message(log_text, f"🛑 All numbers processed, stopping workers...\n")
    for _ in range(concurrency):
        try:
            number_queue.put(None, timeout=0.1)
        except:
            pass
    
    # Wait for all workers to finish (with timeout)
    for worker in worker_threads:
        worker.join(timeout=2 if running else 0.5)
    
    # Mark as not running only if we weren't already stopped
    if running:
        running = False
    log_message(log_text, f"\n✅ Done. Total success: {len(success_numbers)}\n")
    result_box.delete("1.0", "end")
    result_box.insert("1.0", "\n".join(success_numbers))
    with stats_lock:
        checked = stats["checked"]
        otp = stats["otp_sent"]
        no_acc = stats["no_account"]
    update_stats(stats_labels, checked, total, otp, no_acc)
    log_message(log_text, f"📊 Final Stats - Checked: {checked}, OTP Sent: {otp}, No Account: {no_acc}\n")
    progress.set(1.0)
    
    if stop_btn:
        stop_btn.configure(state="disabled")
    if start_btn:
        start_btn.configure(state="normal")

def stop_bot(log_text, stop_btn=None, start_btn=None):
    global running, browser_windows, active_tabs, number_queue, worker_threads, bot_thread
    
    # Set running to False immediately
    running = False
    log_message(log_text, "🛑 EMERGENCY STOP - Terminating all operations...\n")
    
    # Wait for the main bot thread to finish (if it exists and is running)
    if bot_thread and bot_thread.is_alive():
        log_message(log_text, "⏳ Waiting for main bot thread to finish...\n")
        bot_thread.join(timeout=3)  # Wait up to 3 seconds for graceful shutdown
        if bot_thread.is_alive():
            log_message(log_text, "⚠️ Main thread still running, forcing cleanup...\n")
    
    # Clear the queue with timeout
    cleared_count = 0
    start_clear = time.time()
    while not number_queue.empty() and (time.time() - start_clear) < 2:
        try:
            number_queue.get_nowait()
            number_queue.task_done()
            cleared_count += 1
        except:
            break
    
    if cleared_count > 0:
        log_message(log_text, f"🗑️ Cleared {cleared_count} pending numbers from queue\n")
    
    # Send poison pills to stop workers immediately
    poison_count = max(len(worker_threads), 30)  # Send enough to stop all workers
    for _ in range(poison_count):
        try:
            number_queue.put(None, timeout=0.1)
        except:
            pass
    
    # Wait for worker threads to finish (with short timeout for immediate stop)
    log_message(log_text, f"⏳ Waiting for {len(worker_threads)} worker threads to finish...\n")
    for worker in worker_threads:
        try:
            worker.join(timeout=1)  # Reduced from 3s to 1s for faster stop
        except:
            pass
    
    # Clear worker threads list
    worker_threads.clear()
    log_message(log_text, f"✅ All worker threads stopped\n")
    
    closed_count = 0
    
    # Method 1: Close all tracked tabs from active_tabs (with timeout per tab)
    with tab_lock:
        tabs_to_close = list(active_tabs.items())
    
    log_message(log_text, f"🛑 Closing {len(tabs_to_close)} active tabs...\n")
    
    import concurrent.futures
    def force_close_driver(tab_info):
        try:
            tab_info['driver'].quit()
            return 1
        except:
            return 0
    
    # Close all tabs in parallel with timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(force_close_driver, tab_info) for _, tab_info in tabs_to_close]
        try:
            for future in concurrent.futures.as_completed(futures, timeout=5):
                try:
                    closed_count += future.result(timeout=0.5)
                except:
                    pass
        except concurrent.futures.TimeoutError:
            # Some browsers didn't close in time, but continue anyway
            log_message(log_text, f"⚠️ Some browsers slow to close, forcing cleanup...\n")
            pass
    
    # Clear active tabs
    with tab_lock:
        active_tabs.clear()
    
    # Method 2: Close all browsers in browser_windows list
    log_message(log_text, f"🛑 Closing {len(browser_windows)} browser windows...\n")
    for driver in browser_windows[:]:
        try:
            driver.quit()
            closed_count += 1
        except:
            pass
    
    browser_windows.clear()
    
    # Clear all global state variables
    success_numbers.clear()
    with number_status_lock:
        number_status.clear()
    
    # Force garbage collection to free memory
    import gc
    gc.collect()
    
    log_message(log_text, f"✅ STOPPED! Force closed {closed_count} tabs/browsers.\n")
    log_message(log_text, f"✅ All operations terminated. Memory freed.\n")
    log_message(log_text, f"✅ System ready for restart\n")
    
    # Disable stop button and re-enable start button immediately
    if stop_btn:
        stop_btn.configure(state="disabled")
    if start_btn:
        start_btn.configure(state="normal")

def copy_results(result_box):
    data = result_box.get("1.0", "end-1c").strip()
    if data:
        pyperclip.copy(data)
        messagebox.showinfo("Copied", "✅ Successfully copied all successful numbers!")
    else:
        messagebox.showwarning("Empty", "No successful numbers to copy.")

def toggle_headless_mode(enabled):
    global hidden_mode
    hidden_mode = enabled

def update_stats(labels, checked, total, otp_sent=0, no_account=0):
    try:
        remaining = total - checked
        labels["total"].configure(text=f"{total}")
        labels["otp_sent"].configure(text=f"{otp_sent}")
        labels["no_account"].configure(text=f"{no_account}")
        
        # Update tab statistics
        if "active_tabs" in labels:
            total_tabs, working_tabs, idle_tabs = get_tab_info()
            labels["active_tabs"].configure(text=f"{total_tabs} ({working_tabs}W/{idle_tabs}I)")
        
        # Force immediate refresh of all labels
        for label in labels.values():
            try:
                label.update_idletasks()
                label.update()
            except:
                pass
    except:
        pass  # Ignore update errors during UI refresh

# =====================================================
# �🎨 MODERN GUI
# =====================================================

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("📱 FB Recovery Bot - All-In-One Edition")
    root.geometry("950x1000")
    root.resizable(False, False)
    root.configure(fg_color="#F5F7FA")

    # Header
    header_frame = ctk.CTkFrame(root, height=85, fg_color="#F5F7FA", corner_radius=0)
    header_frame.pack(fill="x", pady=0)
    header_frame.pack_propagate(False)

    header_container = ctk.CTkFrame(header_frame, fg_color="transparent")
    header_container.pack(expand=True, pady=15)

    title_container = ctk.CTkFrame(header_container, fg_color="transparent")
    title_container.pack()

    title_label = ctk.CTkLabel(
        title_container, 
        text="📱 FB RECOVERY BOT", 
        font=ctk.CTkFont(family="SF Pro Display", size=24, weight="bold"),
        text_color="#2D3436"
    )
    title_label.pack(side="left", padx=5)

    subtitle_label = ctk.CTkLabel(
        header_container,
        text="All-In-One Edition • Auto Proxy • Queue System",
        font=ctk.CTkFont(family="SF Pro Text", size=12),
        text_color="#636E72"
    )
    subtitle_label.pack(pady=(5, 0))

    # Main container
    main_container = ctk.CTkScrollableFrame(root, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=25, pady=20)

    # Input Section
    input_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E8EAED")
    input_section.pack(fill="both", expand=True, pady=(0, 18))

    input_header = ctk.CTkFrame(input_section, fg_color="transparent")
    input_header.pack(fill="x", padx=25, pady=(20, 15))

    input_icon = ctk.CTkLabel(input_header, text="📞", font=ctk.CTkFont(size=24))
    input_icon.pack(side="left", padx=(0, 10))

    input_label = ctk.CTkLabel(
        input_header,
        text="Phone Numbers",
        font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
        text_color="#2D3436"
    )
    input_label.pack(side="left")

    input_sublabel = ctk.CTkLabel(
        input_section,
        text="Enter one phone number per line",
        font=ctk.CTkFont(family="SF Pro Text", size=13),
        text_color="#636E72"
    )
    input_sublabel.pack(padx=25, anchor="w")

    # Input textbox
    input_box = ctk.CTkTextbox(
        input_section,
        height=120,
        font=ctk.CTkFont(family="SF Mono", size=13),
        fg_color="#F8F9FA",
        text_color="#2D3436",
        border_width=0,
        corner_radius=15,
        scrollbar_button_color="#6C5CE7",
        scrollbar_button_hover_color="#5F4FD1"
    )
    input_box.pack(pady=(10, 15), padx=25, fill="both", expand=True)
    input_box.insert("1.0", "01234567890\n01987654321\n01555555555")

    # Action Buttons
    buttons_frame = ctk.CTkFrame(input_section, fg_color="transparent")
    buttons_frame.pack(fill="x", pady=(0, 15), padx=25)

    def validate_and_start():
        global bot_thread
        numbers = input_box.get("1.0", "end-1c").strip()
        if not numbers:
            CTkMessagebox(title="⚠️ Input Required", message="Please enter phone numbers.", icon="warning", option_1="OK")
            return
        
        # Create and track the bot thread
        bot_thread = threading.Thread(
            target=run_bot,
            args=(numbers.splitlines(), log_text, result_box, progress, stats_labels, concurrency_var, proxy_enabled_var, proxy_var, stop_btn, start_btn, ip_status_label),
            daemon=False
        )
        bot_thread.start()
    
    start_btn = ctk.CTkButton(
        buttons_frame,
        text="▶️  START BOT",
        font=ctk.CTkFont(family="SF Pro Text", size=15, weight="bold"),
        fg_color="#6C5CE7",
        hover_color="#5F4FD1",
        text_color="white",
        height=45,
        corner_radius=15,
        command=validate_and_start
    )
    start_btn.pack(fill="x", pady=(0, 8))

    secondary_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
    secondary_container.pack(fill="x")

    stop_btn = ctk.CTkButton(
        secondary_container,
        text="⏹️  STOP",
        font=ctk.CTkFont(family="SF Pro Text", size=13, weight="bold"),
        fg_color="#FF7675",
        hover_color="#FF6B6B",
        text_color="white",
        height=40,
        corner_radius=13,
        state="disabled",
        command=lambda: stop_bot(log_text, stop_btn, start_btn)
    )
    stop_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

    copy_btn = ctk.CTkButton(
        secondary_container,
        text="📄  COPY",
        font=ctk.CTkFont(family="SF Pro Text", size=13, weight="bold"),
        fg_color="#00B894",
        hover_color="#00A383",
        text_color="white",
        height=40,
        corner_radius=13,
        command=lambda: copy_results(result_box)
    )
    copy_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

    # Settings Section
    settings_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E8EAED")
    settings_frame.pack(fill="x", pady=(0, 18))

    settings_header = ctk.CTkFrame(settings_frame, fg_color="transparent")
    settings_header.pack(fill="x", padx=25, pady=(15, 10))

    settings_icon = ctk.CTkLabel(settings_header, text="⚙️", font=ctk.CTkFont(size=24))
    settings_icon.pack(side="left", padx=(0, 10))

    settings_label = ctk.CTkLabel(
        settings_header,
        text="Configuration",
        font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
        text_color="#2D3436"
    )
    settings_label.pack(side="left")

    # Concurrent Windows
    concurrency_frame = ctk.CTkFrame(settings_frame, fg_color="#F8F9FA", corner_radius=15)
    concurrency_frame.pack(pady=(0, 12), padx=25, fill="x", ipady=15)

    concurrency_inner = ctk.CTkFrame(concurrency_frame, fg_color="transparent")
    concurrency_inner.pack(padx=20)

    ctk.CTkLabel(
        concurrency_inner,
        text="Concurrent Windows",
        font=ctk.CTkFont(family="SF Pro Text", size=14, weight="bold"),
        text_color="#2D3436"
    ).pack(side="left", padx=(0, 15))

    concurrency_var = ctk.StringVar(value="3")
    concurrency_entry = ctk.CTkEntry(
        concurrency_inner,
        textvariable=concurrency_var,
        width=70,
        height=40,
        font=ctk.CTkFont(family="SF Mono", size=16, weight="bold"),
        fg_color="white",
        text_color="#2D3436",
        border_color="#DFE6E9",
        border_width=2,
        corner_radius=12,
        justify="center"
    )
    concurrency_entry.pack(side="left", padx=(0, 15))

    ctk.CTkLabel(
        concurrency_inner,
        text="Max: 30",
        font=ctk.CTkFont(family="SF Pro Text", size=13),
        text_color="#636E72"
    ).pack(side="left")

    # Proxy Configuration
    proxy_config_frame = ctk.CTkFrame(settings_frame, fg_color="#F8F9FA", corner_radius=15)
    proxy_config_frame.pack(pady=(0, 12), padx=25, fill="x", ipady=15)

    proxy_config_inner = ctk.CTkFrame(proxy_config_frame, fg_color="transparent")
    proxy_config_inner.pack(padx=20, fill="x")

    proxy_header = ctk.CTkFrame(proxy_config_inner, fg_color="transparent")
    proxy_header.pack(fill="x", pady=(0, 10))

    proxy_label_frame = ctk.CTkFrame(proxy_header, fg_color="transparent")
    proxy_label_frame.pack(side="left", fill="x", expand=True)

    ctk.CTkLabel(
        proxy_label_frame,
        text="🌐 Custom Proxy Server (Auto-Start)",
        font=ctk.CTkFont(family="SF Pro Text", size=14, weight="bold"),
        text_color="#2D3436"
    ).pack(anchor="w")

    ctk.CTkLabel(
        proxy_label_frame,
        text="Enter your proxy • Format: host:port:user:pass • Runs on localhost:8889",
        font=ctk.CTkFont(family="SF Pro Text", size=11),
        text_color="#636E72"
    ).pack(anchor="w", pady=(2, 0))

    # Load cached proxy or use default
    def load_cached_proxy():
        cache_file = os.path.join(os.path.expanduser("~"), ".fb_bot_proxy_cache")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return f.read().strip()
        except:
            pass
        return DEFAULT_PROXY
    
    # Proxy toggle handler
    def handle_proxy_toggle():
        """Handle proxy toggle ON/OFF with IP display updates"""
        is_enabled = proxy_enabled_var.get()
        
        if is_enabled:
            # User toggled proxy ON
            proxy_address = proxy_var.get().strip()
            if proxy_address:
                save_proxy_cache(proxy_address)
                
            log_message(log_text, f"🌐 Proxy toggle ON - starting proxy...\n")
            if start_local_proxy(proxy_address):
                log_message(log_text, f"✅ Proxy started on localhost:8889\n")
                # Check proxy IP
                log_message(log_text, f"🔍 Checking proxy IP...\n")
                proxy_ip = check_proxy_ip()
                ip_status_label.configure(text=f"Current IP: {proxy_ip} (via proxy)", text_color="#00B894")
                log_message(log_text, f"✅ Connected via proxy: {proxy_ip}\n")
            else:
                log_message(log_text, f"⚠️ Proxy failed to start\n")
                ip_status_label.configure(text="Current IP: Proxy failed", text_color="#FF7675")
        else:
            # User toggled proxy OFF
            log_message(log_text, f"🔴 Proxy toggle OFF - stopping proxy...\n")
            stop_local_proxy()
            log_message(log_text, f"✅ Proxy stopped\n")
            # Check system IP
            log_message(log_text, f"🔍 Checking system IP...\n")
            system_ip = check_current_ip()
            ip_status_label.configure(text=f"Current IP: {system_ip} (direct)", text_color="#6C5CE7")
            log_message(log_text, f"✅ Direct connection: {system_ip}\n")

    proxy_enabled_var = ctk.BooleanVar(value=False)
    proxy_var = ctk.StringVar(value=load_cached_proxy())
    
    proxy_switch = ctk.CTkSwitch(
        proxy_header,
        text="",
        variable=proxy_enabled_var,
        onvalue=True,
        offvalue=False,
        width=50,
        height=26,
        fg_color="#DFE6E9",
        progress_color="#6C5CE7",
        button_color="white",
        command=handle_proxy_toggle
    )
    proxy_switch.pack(side="right", padx=(15, 0))

    # Proxy input field
    proxy_input_frame = ctk.CTkFrame(proxy_config_inner, fg_color="transparent")
    proxy_input_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        proxy_input_frame,
        text="Proxy Address:",
        font=ctk.CTkFont(family="SF Pro Text", size=12),
        text_color="#636E72"
    ).pack(anchor="w", pady=(0, 5))

    proxy_entry = ctk.CTkEntry(
        proxy_input_frame,
        textvariable=proxy_var,
        placeholder_text="host:port:username:password",
        width=500,
        height=40,
        font=ctk.CTkFont(family="SF Mono", size=11),
        fg_color="white",
        text_color="#2D3436",
        border_color="#DFE6E9",
        border_width=2,
        corner_radius=12
    )
    proxy_entry.pack(fill="x")

    # IP Display
    ip_display_frame = ctk.CTkFrame(proxy_config_inner, fg_color="transparent")
    ip_display_frame.pack(fill="x", pady=(10, 0))

    ip_status_label = ctk.CTkLabel(
        ip_display_frame,
        text="Current IP: Checking...",
        font=ctk.CTkFont(family="SF Mono", size=11, weight="bold"),
        text_color="#6C5CE7"
    )
    ip_status_label.pack(anchor="w")

    # Headless Mode
    headless_frame = ctk.CTkFrame(settings_frame, fg_color="#F8F9FA", corner_radius=15)
    headless_frame.pack(pady=(0, 20), padx=25, fill="x", ipady=15)

    headless_inner = ctk.CTkFrame(headless_frame, fg_color="transparent")
    headless_inner.pack(padx=20, fill="x")

    headless_label_frame = ctk.CTkFrame(headless_inner, fg_color="transparent")
    headless_label_frame.pack(side="left", fill="x", expand=True)

    ctk.CTkLabel(
        headless_label_frame,
        text="👻 Headless Mode",
        font=ctk.CTkFont(family="SF Pro Text", size=14, weight="bold"),
        text_color="#2D3436"
    ).pack(anchor="w")

    ctk.CTkLabel(
        headless_label_frame,
        text="Hide browser windows automatically",
        font=ctk.CTkFont(family="SF Pro Text", size=11),
        text_color="#636E72"
    ).pack(anchor="w", pady=(2, 0))

    headless_var = ctk.BooleanVar(value=False)
    headless_switch = ctk.CTkSwitch(
        headless_inner,
        text="",
        variable=headless_var,
        onvalue=True,
        offvalue=False,
        width=50,
        height=26,
        fg_color="#DFE6E9",
        progress_color="#6C5CE7",
        button_color="white",
        command=lambda: toggle_headless_mode(headless_var.get())
    )
    headless_switch.pack(side="right", padx=(15, 0))

    # Stats Cards
    stats_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E8EAED")
    stats_section.pack(fill="x", pady=(0, 15))

    stats_header = ctk.CTkFrame(stats_section, fg_color="transparent")
    stats_header.pack(fill="x", padx=25, pady=(12, 8))

    stats_icon = ctk.CTkLabel(stats_header, text="📊", font=ctk.CTkFont(size=24))
    stats_icon.pack(side="left", padx=(0, 10))

    stats_title = ctk.CTkLabel(
        stats_header,
        text="Live Statistics",
        font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
        text_color="#2D3436"
    )
    stats_title.pack(side="left")

    stats_container = ctk.CTkFrame(stats_section, fg_color="transparent")
    stats_container.pack(pady=(0, 12), padx=25, fill="x")

    stats_labels = {}
    
    stat_configs = [
        ("total", "📦 Total Numbers", "#6C5CE7", "#A29BFE"),
        ("otp_sent", "✅ OTP Sent", "#00B894", "#55EFC4"),
        ("no_account", "❌ No Account", "#FF7675", "#FFA8A8"),
        ("active_tabs", "🆔 Active Tabs", "#0984E3", "#74B9FF")
    ]
    
    for idx, (key, text, color1, color2) in enumerate(stat_configs):
        stat_card = ctk.CTkFrame(stats_container, fg_color="#F8F9FA", corner_radius=15, border_width=1, border_color="#E8EAED")
        stat_card.grid(row=0, column=idx, padx=6, pady=0, sticky="ew")
        stats_container.grid_columnconfigure(idx, weight=1)
        
        ctk.CTkLabel(
            stat_card,
            text=text,
            font=ctk.CTkFont(family="SF Pro Text", size=12, weight="bold"),
            text_color="#636E72"
        ).pack(pady=(14, 6))
        
        stats_labels[key] = ctk.CTkLabel(
            stat_card,
            text="0",
            font=ctk.CTkFont(family="SF Pro Display", size=28, weight="bold"),
            text_color=color1
        )
        stats_labels[key].pack(pady=(0, 14))

    # Progress Bar
    progress_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E8EAED")
    progress_section.pack(fill="x", pady=(0, 15))

    progress_header = ctk.CTkFrame(progress_section, fg_color="transparent")
    progress_header.pack(fill="x", padx=25, pady=(12, 8))

    progress_icon = ctk.CTkLabel(progress_header, text="⏳", font=ctk.CTkFont(size=24))
    progress_icon.pack(side="left", padx=(0, 10))

    progress_label = ctk.CTkLabel(
        progress_header,
        text="Progress",
        font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
        text_color="#2D3436"
    )
    progress_label.pack(side="left")

    progress = ctk.CTkProgressBar(
        progress_section,
        height=14,
        corner_radius=8,
        fg_color="#F8F9FA",
        progress_color="#6C5CE7",
        border_width=0
    )
    progress.pack(pady=(0, 12), padx=25, fill="x")
    progress.set(0)

    # Log Section
    log_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E8EAED")
    log_section.pack(fill="both", expand=True, pady=(0, 15))

    log_header = ctk.CTkFrame(log_section, fg_color="transparent")
    log_header.pack(fill="x", padx=25, pady=(12, 8))

    log_icon = ctk.CTkLabel(log_header, text="📝", font=ctk.CTkFont(size=24))
    log_icon.pack(side="left", padx=(0, 10))

    log_label = ctk.CTkLabel(
        log_header,
        text="Activity Log",
        font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
        text_color="#2D3436"
    )
    log_label.pack(side="left")

    # Log textbox
    log_text = ctk.CTkTextbox(
        log_section,
        height=100,
        font=ctk.CTkFont(family="SF Mono", size=11),
        fg_color="#F8F9FA",
        text_color="#636E72",
        border_width=0,
        corner_radius=15,
        scrollbar_button_color="#6C5CE7"
    )
    log_text.pack(pady=(0, 12), padx=25, fill="both", expand=True)
    log_text.insert("1.0", "✨ FB Recovery Bot Initialized\n")
    log_text.insert("end", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    log_text.insert("end", "Ready to process numbers. Click START to begin.\n")
    log_text.insert("end", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
    log_text.configure(state="disabled")

    # Results Section
    results_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E8EAED")
    results_section.pack(fill="both", expand=True, pady=(0, 15))

    results_header = ctk.CTkFrame(results_section, fg_color="transparent")
    results_header.pack(fill="x", padx=25, pady=(12, 8))

    results_icon = ctk.CTkLabel(results_header, text="✅", font=ctk.CTkFont(size=24))
    results_icon.pack(side="left", padx=(0, 10))

    results_label = ctk.CTkLabel(
        results_header,
        text="Successful Numbers",
        font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
        text_color="#00B894"
    )
    results_label.pack(side="left")

    # Results textbox
    result_box = ctk.CTkTextbox(
        results_section,
        height=140,
        font=ctk.CTkFont(family="SF Mono", size=12, weight="bold"),
        fg_color="#E8FAF6",
        text_color="#00B894",
        border_width=0,
        corner_radius=15,
        scrollbar_button_color="#00B894"
    )
    result_box.pack(pady=(0, 20), padx=25, fill="both", expand=True)

    def on_closing():
        global running
        running = False
        stop_local_proxy()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Initialize IP display on startup
    def init_ip_display():
        """Check and display system IP on startup"""
        log_message(log_text, f"🔍 Initializing IP check...\n")
        system_ip = check_current_ip()
        ip_status_label.configure(text=f"Current IP: {system_ip} (direct)", text_color="#6C5CE7")
        log_message(log_text, f"✅ System IP: {system_ip}\n")
        log_message(log_text, f"ℹ️  Bot ready to start!\n")
    
    # Check IP after UI is displayed
    root.after(1000, init_ip_display)
    
    root.mainloop()

if __name__ == "__main__":
    # Initialize anti-debug protection FIRST (before any output)
    protection_enabled = True
    try:
        from protection import init_protection, verify_environment, ProtectionSystem
        
        # Create protection instance and do immediate check
        protection = ProtectionSystem()
        
        # Check for debuggers BEFORE any GUI or license check
        if protection.check_debugger_attached():
            print("\n" + "="*60)
            print("❌ SECURITY ALERT: Debugger detected (attached)")
            print("Application cannot run while debugging tools are active.")
            print("="*60 + "\n")
            protection.silent_exit()
        
        if protection.check_debugger_processes():
            print("\n" + "="*60)
            print("❌ SECURITY ALERT: Debugging software detected")
            print("Please close all debugging tools and try again.")
            print("="*60 + "\n")
            protection.silent_exit()
        
        if protection.check_vm_environment():
            print("\n" + "="*60)
            print("⚠️  WARNING: Virtual machine detected")
            print("="*60 + "\n")
            # Allow VM but log it
        
        # Verify environment is safe
        verify_environment()
        # Start continuous monitoring
        init_protection()
        
    except ImportError:
        protection_enabled = False
        print("⚠️  Warning: Protection module not available")
    except SystemExit:
        # Let protection system exit naturally
        raise
    except:
        # Silent exit on any protection error
        import os
        os._exit(1)
    
    print("=" * 60)
    print("  FB RECOVERY BOT - ALL-IN-ONE EDITION")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print("  Embedded Proxy: Auto-Start Enabled")
    print("  License Protection: Active")
    print("=" * 60)
    
    # Show license verification window first
    try:
        from license_ui import show_license_window
        show_license_window(main)
    except ImportError as e:
        print(f"❌ License module not found: {e}")
        print("Running without license protection...")
        main()
    except Exception as e:
        print(f"❌ License verification error: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)
