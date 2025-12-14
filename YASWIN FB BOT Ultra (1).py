# =====================================================
# 💙 FB RECOVER BOT BY YASHWIN KHAN (Premium GUI Edition 2025 v2 - FIXED)
# =====================================================
# pip install selenium webdriver-manager keyboard pyperclip pygetwindow

import os, threading, time, random, pyperclip, pygetwindow as gw
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG ==================
URL = "https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0"
MAX_CONCURRENCY = 30
WINDOW_SIZE = (980, 720)
STAGGER = 40
# ===========================================

success_numbers = []
running = False
hidden_mode = False
chrome_windows = []

# ===== Utility =====
def human_type(element, text, min_delay=0.03, max_delay=0.1):
    try:
        element.clear()
    except:
        pass
    for ch in text:
        try:
            element.send_keys(ch)
        except:
            pass
        time.sleep(random.uniform(min_delay, max_delay))

# ===== Input Finders =====
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
    texts = ["Search", "Continue", "Find", "Next"]
    for t in texts:
        try:
            el = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(),"{t}")]'))
            )
            if el.is_displayed():
                return el
        except:
            pass
    return None

def check_send_sms(driver):
    try:
        el = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//label[contains(., "SMS") or contains(., "Send via SMS")]'))
        )
        return el if el.is_displayed() else None
    except:
        return None

def find_send_button(driver):
    try:
        el = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Send") or contains(., "Continue")]'))
        )
        return el
    except:
        return None

# ===== MAIN WORK (FIXED) =====
def handle_window(driver, number, log_text, stats):
    try:
        driver.get(URL)
        time.sleep(random.uniform(1, 2))

        input_el = find_input(driver)
        if not input_el:
            log_text.insert(tk.END, f"{number}: ❌ Input box not found\n")
            driver.quit()
            return

        input_el.click()
        human_type(input_el, number)
        time.sleep(0.6)

        btn = find_search_button(driver)
        if btn:
            btn.click()
        else:
            input_el.send_keys(Keys.ENTER)

        time.sleep(3)

        sms_option = check_send_sms(driver)
        if sms_option:
            driver.execute_script("arguments[0].click();", sms_option)
            log_text.insert(tk.END, f"{number}: 🔹 SMS option selected\n")
            time.sleep(1.5)

            send_btn = find_send_button(driver)
            if send_btn:
                log_text.insert(tk.END, f"{number}: 🟢 Send button found, sending...\n")
                driver.execute_script("arguments[0].click();", send_btn)

                # wait a bit for SMS to actually send
                time.sleep(15)
                success_numbers.append(number)
                log_text.insert(tk.END, f"{number}: ✅ SMS sent successfully!\n")
            else:
                log_text.insert(tk.END, f"{number}: ⚠ SMS option found but no Send button visible\n")
                time.sleep(2)
        else:
            log_text.insert(tk.END, f"{number}: ❌ No SMS option found\n")
            time.sleep(2)

        log_text.see(tk.END)

    except Exception as e:
        log_text.insert(tk.END, f"{number}: ❌ Error: {e}\n")
    finally:
        try:
            driver.quit()
        except:
            pass
        stats["checked"] += 1

# ===== Browser Starter =====
def open_browser_instance(index, number, log_text, stats):
    opts = webdriver.ChromeOptions()
    opts.add_argument("--disable-notifications")
    opts.add_argument(f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}")
    opts.add_argument(f"--window-position={index * STAGGER},{index * STAGGER}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    chrome_windows.append(driver)
    if hidden_mode:
        try:
            for w in gw.getWindowsWithTitle("Chrome"):
                w.minimize()
        except:
            pass
    handle_window(driver, number, log_text, stats)

# ===== Runner =====
def run_bot(numbers, log_text, result_box, progress, stats_labels, concurrency_var):
    global running
    if running:
        return
    running = True
    success_numbers.clear()
    log_text.insert(tk.END, f"🔹 Starting bot with {len(numbers)} numbers...\n")

    total = len(numbers)
    stats = {"checked": 0}
    concurrency = min(int(concurrency_var.get()), MAX_CONCURRENCY)

    i = 0
    while i < len(numbers) and running:
        threads = []
        batch = numbers[i:i + concurrency]
        for idx, num in enumerate(batch):
            if num.strip() == "":
                continue
            t = threading.Thread(target=open_browser_instance, args=(idx, num, log_text, stats))
            t.start()
            threads.append(t)
            time.sleep(0.5)
        for t in threads:
            t.join()
        i += concurrency

        update_stats(stats_labels, stats["checked"], total)
        progress["value"] = (stats["checked"] / total) * 100
        progress.update()

    running = False
    log_text.insert(tk.END, f"\n✅ Done. Total success: {len(success_numbers)}\n")
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, "\n".join(success_numbers))
    update_stats(stats_labels, stats["checked"], total)
    progress["value"] = 100

def stop_bot(log_text):
    global running
    running = False
    log_text.insert(tk.END, "🛑 Bot stopped by user.\n")

def copy_results(result_box):
    data = result_box.get("1.0", tk.END).strip()
    if data:
        pyperclip.copy(data)
        messagebox.showinfo("Copied", "✅ Successfully copied all successful numbers!")
    else:
        messagebox.showwarning("Empty", "No successful numbers to copy.")

def toggle_windows(btn):
    global hidden_mode
    hidden_mode = not hidden_mode
    if hidden_mode:
        for w in gw.getWindowsWithTitle("Chrome"):
            try:
                w.minimize()
            except:
                pass
        btn.config(text="🟢 SHOW WINDOWS", bg="#00ff88")
    else:
        for w in gw.getWindowsWithTitle("Chrome"):
            try:
                w.restore()
            except:
                pass
        btn.config(text="🔴 HIDE WINDOWS", bg="#ff4444")

def update_stats(labels, checked, total):
    remaining = total - checked
    labels["total"].config(text=f"Total: {total}")
    labels["checked"].config(text=f"Checked: {checked}")
    labels["remain"].config(text=f"Remaining: {remaining}")

# ===== GUI =====
def main():
    root = tk.Tk()
    root.title("FB Recover Bot by Yashwin Khan")
    root.geometry("800x780")
    root.configure(bg="#0b132b")

    title_frame = tk.Frame(root, bg="#0b132b")
    title_frame.pack(pady=10)

    tk.Label(title_frame, text="🌐", font=("Segoe UI", 18), bg="#0b132b", fg="#00aaff").pack(side="left", padx=5)
    tk.Label(title_frame, text="FB RECOVER BOT", font=("Segoe UI", 18, "bold"), bg="#0b132b", fg="#C0C0C0").pack(side="left")
    tk.Label(title_frame, text="✔", font=("Segoe UI", 18), bg="#0b132b", fg="#00aaff").pack(side="left", padx=5)

    tk.Label(root, text="Premium Edition by Yashwin Khan", font=("Segoe UI", 10, "italic"), bg="#0b132b", fg="#ffffff").pack()

    tk.Label(root, text="📋 Enter your number list (one per line):", bg="#0b132b", fg="#ffffff", font=("Segoe UI", 11, "bold")).pack()
    input_box = scrolledtext.ScrolledText(root, width=75, height=8, font=("Consolas", 10))
    input_box.pack(pady=5)

    control_frame = tk.Frame(root, bg="#0b132b")
    control_frame.pack(pady=5)
    tk.Label(control_frame, text="Windows to open:", bg="#0b132b", fg="#ffffff", font=("Segoe UI", 10, "bold")).pack(side="left")
    concurrency_var = tk.StringVar(value="3")
    tk.Entry(control_frame, textvariable=concurrency_var, width=5, font=("Consolas", 11)).pack(side="left", padx=5)
    tk.Label(control_frame, text="(max 30)", bg="#0b132b", fg="#888888").pack(side="left")

    # ===== Progress and Stats =====
    stats_frame = tk.Frame(root, bg="#0b132b")
    stats_frame.pack(pady=5)
    stats_labels = {
        "total": tk.Label(stats_frame, text="Total: 0", bg="#0b132b", fg="#ffffff", font=("Segoe UI", 10, "bold")),
        "checked": tk.Label(stats_frame, text="Checked: 0", bg="#0b132b", fg="#00aaff", font=("Segoe UI", 10, "bold")),
        "remain": tk.Label(stats_frame, text="Remaining: 0", bg="#0b132b", fg="#ff5555", font=("Segoe UI", 10, "bold"))
    }
    stats_labels["total"].grid(row=0, column=0, padx=10)
    stats_labels["checked"].grid(row=0, column=1, padx=10)
    stats_labels["remain"].grid(row=0, column=2, padx=10)

    progress = ttk.Progressbar(root, length=600, mode='determinate')
    progress.pack(pady=10)

    # ===== Log + Results =====
    log_text = scrolledtext.ScrolledText(root, width=75, height=10, bg="#1c2541", fg="#ffffff", font=("Consolas", 10))
    log_text.pack(pady=10)
    log_text.insert(tk.END, "🔹 Status log will appear here...\n")

    result_box = scrolledtext.ScrolledText(root, width=75, height=6, bg="#1c2541", fg="#00ff99", font=("Consolas", 10))
    result_box.pack(pady=10)

    # ===== Buttons =====
    frame = tk.Frame(root, bg="#0b132b")
    frame.pack(pady=10)

    tk.Button(frame, text="▶ START BOT", bg="#00aaff", fg="white", font=("Segoe UI", 11, "bold"),
              command=lambda: threading.Thread(
                  target=run_bot,
                  args=(input_box.get("1.0", tk.END).splitlines(), log_text, result_box, progress, stats_labels, concurrency_var)
              ).start()).grid(row=0, column=0, padx=10)

    tk.Button(frame, text="⛔ STOP BOT", bg="#ff3333", fg="white", font=("Segoe UI", 11, "bold"),
              command=lambda: stop_bot(log_text)).grid(row=0, column=1, padx=10)

    toggle_btn = tk.Button(frame, text="🔴 HIDE WINDOWS", bg="#ff4444", fg="white",
                           font=("Segoe UI", 11, "bold"),
                           command=lambda: toggle_windows(toggle_btn))
    toggle_btn.grid(row=0, column=2, padx=10)

    tk.Button(root, text="📎 COPY SUCCESSFUL NUMBERS", bg="#00ff99", fg="black",
              font=("Segoe UI", 10, "bold"),
              command=lambda: copy_results(result_box)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
