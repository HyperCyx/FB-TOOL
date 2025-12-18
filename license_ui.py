import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import threading
from license_manager import (
    verify_license, save_license, load_license, delete_license,
    start_heartbeat, API_URL, SERVER_API_KEY, PRODUCT_ID
)

class LicenseWindow:
    def __init__(self, on_success_callback):
        self.on_success_callback = on_success_callback
        self.license_key = None
        self.is_verifying = False
        
        # Create window
        self.window = ctk.CTk()
        self.window.title("FB Recovery Bot - License Activation")
        self.window.geometry("600x450")
        self.window.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("light")
        self.window.configure(fg_color="#F5F7FA")
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_ui()
        
        # Check for saved license
        self.check_saved_license()
    
    def center_window(self):
        """Center the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create the license verification UI."""
        # Main container
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E8EAED"
        )
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="🔐 License Activation",
            font=("SF Pro Display", 28, "bold"),
            text_color="#1F2937"
        )
        header_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Enter your license key to activate FB Recovery Bot",
            font=("SF Pro Text", 14),
            text_color="#6B7280"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # License input section
        input_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#F9FAFB",
            corner_radius=12
        )
        input_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        license_label = ctk.CTkLabel(
            input_frame,
            text="License Key",
            font=("SF Pro Text", 13, "bold"),
            text_color="#374151"
        )
        license_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.license_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter your license key here...",
            font=("SF Mono", 13),
            height=45,
            border_width=1,
            border_color="#D1D5DB",
            fg_color="white"
        )
        self.license_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Remember license checkbox
        self.remember_var = ctk.BooleanVar(value=True)
        remember_check = ctk.CTkCheckBox(
            main_frame,
            text="Remember this license key",
            variable=self.remember_var,
            font=("SF Pro Text", 12),
            text_color="#6B7280",
            fg_color="#6C5CE7",
            hover_color="#5B4BD6"
        )
        remember_check.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("SF Pro Text", 12),
            text_color="#6B7280"
        )
        self.status_label.pack(pady=(0, 15))
        
        # Buttons frame
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=(0, 30))
        
        # Activate button
        self.activate_btn = ctk.CTkButton(
            button_frame,
            text="Activate License",
            command=self.verify_license_thread,
            font=("SF Pro Text", 14, "bold"),
            height=45,
            width=180,
            fg_color="#6C5CE7",
            hover_color="#5B4BD6",
            corner_radius=10
        )
        self.activate_btn.pack(side="left", padx=5)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.exit_app,
            font=("SF Pro Text", 14),
            height=45,
            width=120,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=10
        )
        exit_btn.pack(side="left", padx=5)
        
        # Hardware ID display
        hw_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#FEF3C7",
            corner_radius=8
        )
        hw_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        from license_manager import get_hardware_id
        hw_id = get_hardware_id()[:16] + "..."
        
        hw_label = ctk.CTkLabel(
            hw_frame,
            text=f"🖥️ Hardware ID: {hw_id}",
            font=("SF Mono", 11),
            text_color="#92400E"
        )
        hw_label.pack(pady=10)
    
    def check_saved_license(self):
        """Check if there's a saved license and verify it."""
        saved_license = load_license()
        if saved_license:
            self.status_label.configure(text="🔄 Verifying saved license...", text_color="#6C5CE7")
            self.license_entry.insert(0, saved_license)
            self.window.update()
            
            # Verify in background
            threading.Thread(target=self.verify_saved_license, args=(saved_license,), daemon=True).start()
    
    def verify_saved_license(self, license_key):
        """Verify saved license in background."""
        time.sleep(0.5)  # Brief delay for UI update
        is_valid, details, interval = verify_license(SERVER_API_KEY, license_key, PRODUCT_ID, API_URL)
        
        if is_valid:
            self.license_key = license_key
            start_heartbeat(license_key, interval)
            self.window.after(100, self.success_and_close)
        else:
            # Invalid saved license
            self.window.after(100, lambda: self.status_label.configure(
                text=f"❌ Saved license invalid: {details.get('message', 'Unknown error')}",
                text_color="#EF4444"
            ))
            delete_license()
    
    def verify_license_thread(self):
        """Start license verification in separate thread."""
        if self.is_verifying:
            return
        
        license_key = self.license_entry.get().strip()
        
        if not license_key:
            CTkMessagebox(
                title="Error",
                message="Please enter a license key",
                icon="cancel",
                option_1="OK"
            )
            return
        
        self.is_verifying = True
        self.activate_btn.configure(state="disabled", text="Verifying...")
        self.status_label.configure(text="🔄 Verifying license...", text_color="#6C5CE7")
        
        threading.Thread(target=self.verify_license_async, args=(license_key,), daemon=True).start()
    
    def verify_license_async(self, license_key):
        """Verify license asynchronously."""
        is_valid, details, interval = verify_license(SERVER_API_KEY, license_key, PRODUCT_ID, API_URL)
        
        if is_valid:
            # Save license if remember is checked
            if self.remember_var.get():
                save_license(license_key)
            
            self.license_key = license_key
            start_heartbeat(license_key, interval)
            
            self.window.after(100, self.success_and_close)
        else:
            # Show error
            error_msg = details.get('message', 'Unknown error')
            self.window.after(100, lambda: self.show_error(error_msg))
    
    def show_error(self, message):
        """Show error message."""
        self.status_label.configure(text=f"❌ {message}", text_color="#EF4444")
        self.activate_btn.configure(state="normal", text="Activate License")
        self.is_verifying = False
        
        CTkMessagebox(
            title="License Verification Failed",
            message=message,
            icon="cancel",
            option_1="OK"
        )
    
    def success_and_close(self):
        """License verified successfully."""
        self.status_label.configure(text="✅ License verified! Starting application...", text_color="#10B981")
        self.activate_btn.configure(text="✓ Verified")
        
        # Close window and launch main app
        self.window.after(1000, self.launch_main_app)
    
    def launch_main_app(self):
        """Close license window and launch main application."""
        self.window.destroy()
        if self.on_success_callback:
            self.on_success_callback()
    
    def exit_app(self):
        """Exit the application."""
        self.window.destroy()
        import sys
        sys.exit(0)
    
    def run(self):
        """Run the license window."""
        self.window.mainloop()

def show_license_window(on_success_callback):
    """Show license verification window."""
    license_win = LicenseWindow(on_success_callback)
    license_win.run()
