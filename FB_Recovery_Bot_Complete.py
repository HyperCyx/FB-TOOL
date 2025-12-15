#!/usr/bin/env python3
# =====================================================
# 💙 FB RECOVERY BOT - ALL-IN-ONE EDITION
# By: YASHWIN KHAN | Admin: Hyper Red | Developer: HYPER RED
# Cross-Platform: Windows, Linux, Mac
# Auto Proxy Management with Embedded FLUXY
# =====================================================
# Installation:
# pip install selenium webdriver-manager customtkinter CTkMessagebox pyperclip

import os, threading, time, random, pyperclip, zipfile, tempfile, json
import socket, select, base64, sys, platform, subprocess
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
URL = "https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0"
MAX_CONCURRENCY = 30
WINDOW_SIZE = (980, 720)
STAGGER = 40

# Embedded Proxy Configuration (Default - can be overridden from UI)
DEFAULT_PROXY = "c5dc26dff0213e3f.abcproxy.vip:4950:abc5650020_kaqz-zone-abc-region-SL:98459013"
LOCAL_PROXY_PORT = 8889

# Global proxy configuration (set from UI)
current_proxy_config = {
    'host': 'c5dc26dff0213e3f.abcproxy.vip',
    'port': 4950,
    'user': 'abc5650020_kaqz-zone-abc-region-SL',
    'pass': '98459013'
}
# ===========================================

success_numbers = []
running = False
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
    try:
        inputs = driver.find_elements(By.XPATH, '//input[@type="text" or @type="email"]')
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
    # Multilingual button text support
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
    
    # Method 1: Try exact text match
    for t in texts:
        try:
            el = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(),"{t}")]'))
            )
            if el.is_displayed():
                return el
        except:
            pass
    
    # Method 2: Try case-insensitive and partial match
    for t in texts:
        try:
            xpath = f'//button[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{t.lower()}")]'
            el = driver.find_element(By.XPATH, xpath)
            if el.is_displayed() and el.is_enabled():
                return el
        except:
            pass
    
    # Method 3: Try any visible button with type="submit"
    try:
        buttons = driver.find_elements(By.XPATH, '//button[@type="submit"]')
        for btn in buttons:
            if btn.is_displayed() and btn.is_enabled():
                return btn
    except:
        pass
    
    # Method 4: Try any visible button in the form
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
    # Multilingual send/continue button text
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
            el = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[contains(., "{text}")]'))
            )
            if el.is_displayed():
                return el
        except:
            continue
    return None

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
    
    # Maximum execution time for entire operation
    MAX_EXECUTION_TIME = 120  # 2 minutes total per number
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
            return
        
        # Increase timeouts for proxy connections
        if using_proxy:
            driver.set_page_load_timeout(60)  # 60 seconds for proxy
            driver.implicitly_wait(15)
        else:
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
        
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
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped before loading\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return
        
        # Load Facebook with retry on timeout
        max_retries = 2
        for retry in range(max_retries):
            try:
                driver.get(URL)
                time.sleep(random.uniform(2, 3))
                update_activity('working')
                break
            except Exception as e:
                if retry < max_retries - 1:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Page load timeout, retrying...\n")
                    time.sleep(2)
                else:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ Failed to load Facebook page: {str(e)[:50]}\n")
                    update_activity('idle')
                    stats["checked"] += 1
                    return
            
            # Check timeout between retries
            if check_timeout(f"Facebook load retry {retry+1}"):
                stats["checked"] += 1
                return
        
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped during load\n")
            update_activity('stopped')
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

        update_activity('working')
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

        input_el.click()
        human_type(input_el, number)
        update_activity('working')
        time.sleep(0.6)

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

        time.sleep(3)
        update_activity('working')

        # Check timeout after search
        if check_timeout("after search click"):
            with stats_lock:
                stats["checked"] += 1
            return

        # Check for "No search result" or similar messages
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⛔ Stopped after search\n")
            update_activity('stopped')
            try:
                driver.quit()
                unregister_tab(tab_id)
            except:
                pass
            return
        
        try:
            # Check for various "no result" messages
            no_result_indicators = [
                "no search results",
                "no results found",
                "couldn't find",
                "can't find",
                "no matches",
                "does not match",
                "doesn't match",
                "not found",
                "no account found",
                "পাওয়া যায়নি",  # Bengali: Not found
                "ফলাফল নেই"  # Bengali: No result
            ]
            
            page_text = driver.page_source.lower()
            
            for indicator in no_result_indicators:
                if indicator in page_text:
                    log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ❌ No account found - closing tab\n")
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
        sms_option = check_send_sms(driver)
        if sms_option:
            driver.execute_script("arguments[0].click();", sms_option)
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🔹 SMS option selected\n")
            update_activity('working')
            time.sleep(1.5)

            # Check timeout before send button
            if check_timeout("finding send button"):
                with stats_lock:
                    stats["checked"] += 1
                return

            update_activity('working')
            send_btn = find_send_button(driver)
            if send_btn:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🟢 Sending SMS...\n")
                driver.execute_script("arguments[0].click();", send_btn)
                update_activity('working')
                time.sleep(15)
                success_numbers.append(number)
                with stats_lock:
                    stats["otp_sent"] += 1
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ SMS sent successfully!\n")
                update_activity('working')
            else:
                log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠ SMS option found but no Send button - closing tab\n")
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
        # Calculate total execution time
        total_time = time.time() - start_time
        
        # Only close browser in these cases:
        # 1. User manually stopped (not running)
        # 2. OTP was successfully sent
        should_close = False
        
        if not running:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): 🛑 Stopped by user - closing tab\n")
            update_activity('stopped')
            should_close = True
        elif number in success_numbers:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ✅ OTP sent successfully - closing tab in {int(total_time)}s\n")
            update_activity('working')
            should_close = True
        elif total_time > MAX_EXECUTION_TIME:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⏱️ Timeout after {int(total_time)}s - closing tab\n")
            update_activity('stopped')
            if number not in success_numbers:  # Only count if not already counted
                stats["checked"] += 1
            should_close = True
        else:
            log_message(log_text, f"🆔 Tab #{tab_id} ({number}): ⚠️ Issue detected - closing tab\n")
            update_activity('stopped')
            should_close = True
        
        # Only quit driver if should_close is True
        if should_close:
            try:
                driver.quit()
                unregister_tab(tab_id)  # Remove from tracking when closed
            except:
                pass

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
        log_message(log_text, f"{number}: 🚀 Starting Chrome...\n")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
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

def run_bot(numbers, log_text, result_box, progress, stats_labels, concurrency_var, proxy_enabled_var=None, proxy_var=None, stop_btn=None, start_btn=None, ip_label=None):
    global running
    if running:
        return
    running = True
    success_numbers.clear()
    
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
    
    log_message(log_text, f"🔹 Starting bot with {len(numbers)} numbers...\n")

    total = len(numbers)
    stats = {"checked": 0, "otp_sent": 0, "no_account": 0}
    concurrency = min(int(concurrency_var.get()), MAX_CONCURRENCY)

    proxy_config = {'enabled': proxy_enabled} if proxy_enabled else None
    
    i = 0
    while i < len(numbers) and running:
        threads = []
        batch = numbers[i:i + concurrency]
        for idx, num in enumerate(batch):
            if num.strip() == "":
                continue
            t = threading.Thread(target=open_browser_instance, args=(idx, num, log_text, stats, proxy_config))
            t.start()
            threads.append(t)
            # Longer delay between instances when using proxy
            if proxy_config and proxy_config.get('enabled'):
                time.sleep(2)  # 2 seconds for proxy
            else:
                time.sleep(0.5)
        for t in threads:
            t.join()
        i += concurrency

        with stats_lock:
            checked = stats["checked"]
            otp = stats["otp_sent"]
            no_acc = stats["no_account"]
        update_stats(stats_labels, checked, total, otp, no_acc)
        progress.set((checked / total) if total > 0 else 0)
        progress.update()

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
    global running, browser_windows, active_tabs
    
    running = False
    log_message(log_text, "🛑 STOPPING - Force closing all tabs and browsers...\n")
    
    closed_count = 0
    
    # Method 1: Close all tracked tabs from active_tabs
    with tab_lock:
        tabs_to_close = list(active_tabs.items())
    
    for tab_id, tab_info in tabs_to_close:
        try:
            log_message(log_text, f"🛑 Force closing Tab #{tab_id} ({tab_info['number']})\n")
            tab_info['driver'].quit()
            closed_count += 1
        except:
            pass
    
    # Clear active tabs
    with tab_lock:
        active_tabs.clear()
    
    # Method 2: Close all browsers in browser_windows list
    for driver in browser_windows[:]:
        try:
            driver.quit()
            closed_count += 1
        except:
            pass
    
    browser_windows.clear()
    
    log_message(log_text, f"✅ STOPPED! Force closed {closed_count} tabs/browsers.\n")
    log_message(log_text, f"✅ All operations terminated.\n")
    
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
    except:
        pass  # Ignore update errors during UI refresh

# =====================================================
# 🎨 MODERN GUI
# =====================================================

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("FB Recovery Bot - All-In-One Edition")
    root.geometry("950x1000")
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
        text="All-In-One Edition • Auto Proxy • Cross-Platform",
        font=ctk.CTkFont(family="SF Pro Text", size=12),
        text_color="#636E72"
    )
    subtitle_label.pack(pady=(5, 0))

    main_container = ctk.CTkScrollableFrame(root, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=25, pady=20)

    # Input Section
    input_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20)
    input_section.pack(fill="both", expand=True, pady=(0, 20))

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
        numbers = input_box.get("1.0", "end-1c").strip()
        if not numbers:
            CTkMessagebox(title="⚠️ Input Required", message="Please enter phone numbers.", icon="warning", option_1="OK")
            return
        threading.Thread(
            target=run_bot,
            args=(numbers.splitlines(), log_text, result_box, progress, stats_labels, concurrency_var, proxy_enabled_var, proxy_var, stop_btn, start_btn, ip_status_label)
        ).start()
    
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
        height=40,
        corner_radius=13,
        command=lambda: copy_results(result_box)
    )
    copy_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

    # Settings Section
    settings_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20)
    settings_frame.pack(fill="x", pady=(0, 15))

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

    # Proxy Toggle
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
    stats_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20)
    stats_section.pack(fill="x", pady=(0, 12))

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
        stat_card = ctk.CTkFrame(stats_container, fg_color=color2, corner_radius=16)
        stat_card.grid(row=0, column=idx, padx=8, pady=5, sticky="ew")
        stats_container.grid_columnconfigure(idx, weight=1)
        
        ctk.CTkLabel(
            stat_card,
            text=text,
            font=ctk.CTkFont(family="SF Pro Text", size=13, weight="bold"),
            text_color=color1
        ).pack(pady=(15, 5))
        
        stats_labels[key] = ctk.CTkLabel(
            stat_card,
            text="0",
            font=ctk.CTkFont(family="SF Pro Display", size=32, weight="bold"),
            text_color=color1
        )
        stats_labels[key].pack(pady=(0, 15))

    # Progress Bar
    progress_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20)
    progress_section.pack(fill="x", pady=(0, 12))

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
    log_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20)
    log_section.pack(fill="both", expand=True, pady=(0, 12))

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
    log_text.insert("1.0", "✨ Ready to start...\n")
    log_text.configure(state="disabled")

    # Results Section
    results_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=20)
    results_section.pack(fill="both", expand=True, pady=(0, 10))

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
    print("=" * 60)
    print("  FB RECOVERY BOT - ALL-IN-ONE EDITION")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print("  Embedded Proxy: Auto-Start Enabled")
    print("=" * 60)
    main()
