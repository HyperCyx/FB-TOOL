import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import threading
import time
from license_manager import (
    verify_license, save_license, load_license, delete_license,
    API_URL, SERVER_API_KEY, PRODUCT_ID
)

class LicenseWindow:
    def __init__(self, on_success_callback):
        self.on_success_callback = on_success_callback
        self.license_key = None
        self.is_verifying = False
        
        # Create window
        self.window = ctk.CTk()
        self.window.title("FB Recovery Bot - License Activation")
        self.window.geometry("500x420")
        self.window.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("light")
        self.window.configure(fg_color="#F5F7FA")
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_ui()
        
        # Note: License is already checked before showing this window
        # This window only appears if license is missing or invalid
    
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
            corner_radius=15,
            border_width=1,
            border_color="#E8EAED"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="🔐 License Activation",
            font=("SF Pro Display", 24, "bold"),
            text_color="#1F2937"
        )
        header_label.pack(pady=(20, 8))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Enter your license key to activate FB Recovery Bot",
            font=("SF Pro Text", 12),
            text_color="#6B7280"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # License input section
        input_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#F9FAFB",
            corner_radius=10
        )
        input_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        license_label = ctk.CTkLabel(
            input_frame,
            text="License Key",
            font=("SF Pro Text", 12, "bold"),
            text_color="#374151"
        )
        license_label.pack(anchor="w", padx=12, pady=(12, 5))
        
        self.license_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter your license key here...",
            font=("SF Mono", 12),
            height=40,
            border_width=1,
            border_color="#D1D5DB",
            fg_color="white"
        )
        self.license_entry.pack(fill="x", padx=12, pady=(0, 12))
        
        # License is automatically saved (no checkbox needed)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("SF Pro Text", 11),
            text_color="#6B7280"
        )
        self.status_label.pack(pady=(0, 12))
        
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
            font=("SF Pro Text", 15, "bold"),
            height=48,
            width=200,
            fg_color="#6C5CE7",
            hover_color="#5B4BD6",
            corner_radius=10,
            border_width=2,
            border_color="#5B4BD6"
        )
        self.activate_btn.pack(side="left", padx=5)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.exit_app,
            font=("SF Pro Text", 15, "bold"),
            height=48,
            width=130,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=10,
            border_width=2,
            border_color="#DC2626"
        )
        exit_btn.pack(side="left", padx=5)
        
        # Hardware ID display
        hw_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#FEF3C7",
            corner_radius=8
        )
        hw_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        from license_manager import get_hardware_id
        hw_id = get_hardware_id()[:16] + "..."
        
        hw_label = ctk.CTkLabel(
            hw_frame,
            text=f"🖥️ Hardware ID: {hw_id}",
            font=("SF Mono", 10),
            text_color="#92400E"
        )
        hw_label.pack(pady=8)
    

    
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
        is_valid, details = verify_license(SERVER_API_KEY, license_key, PRODUCT_ID, API_URL)
        
        if is_valid:
            # Always save license automatically
            save_license(license_key)
            
            self.license_key = license_key
            
            self.window.after(100, self.success_and_close)
        else:
            # Show error with formatted message
            error_msg = self.format_error_message(details)
            self.window.after(100, lambda: self.show_error(error_msg, details))
    
    def format_error_message(self, details):
        """Format error message based on error type."""
        message = details.get('message', 'Unknown error')
        error_code = details.get('error', '')
        
        # Add specific details based on error type
        if error_code == 'LICENSE_EXPIRED':
            exp_date = details.get('expirationDate', 'unknown')
            if exp_date != 'unknown':
                try:
                    from datetime import datetime
                    exp_dt = datetime.fromisoformat(exp_date.replace('Z', '+00:00'))
                    exp_str = exp_dt.strftime('%B %d, %Y')
                    message = f"License expired on {exp_str}"
                except:
                    pass
        elif 'maximum devices' in message.lower() or 'device limit' in message.lower():
            max_devices = details.get('maxDevices', details.get('currentDevices', ''))
            if max_devices:
                message = f"Device limit reached ({max_devices} devices maximum)"
        elif error_code == 'INVALID_LICENSE':
            message = "License key not found or invalid"
        elif error_code == 'PRODUCT_MISMATCH':
            message = "This license is not valid for this product"
        elif error_code == 'MISSING_API_KEY':
            message = "Configuration error: API key missing"
        
        return message
    
    def show_error(self, message, details=None):
        """Show error message with details."""
        self.status_label.configure(text=f"❌ {message}", text_color="#EF4444")
        self.activate_btn.configure(state="normal", text="Activate License")
        self.is_verifying = False
        
        # Create detailed error message for popup
        popup_message = message
        if details:
            error_code = details.get('error', '')
            if error_code and error_code not in ['NETWORK_ERROR', 'TIMEOUT', 'CONNECTION_ERROR']:
                popup_message += f"\n\nError Code: {error_code}"
            
            # Add helpful hints based on error
            if error_code == 'LICENSE_EXPIRED':
                popup_message += "\n\nPlease contact support to renew your license."
            elif 'DEVICE' in error_code or 'maximum devices' in message.lower():
                popup_message += "\n\nTo use this license on a new device, please deactivate it from another device first."
            elif error_code == 'INVALID_LICENSE':
                popup_message += "\n\nPlease check your license key and try again."
        
        CTkMessagebox(
            title="License Verification Failed",
            message=popup_message,
            icon="cancel",
            option_1="OK",
            width=450
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
    """Show license verification window only if needed."""
    # First, check if there's a saved license
    saved_license = load_license()
    
    if saved_license:
        # Try to verify saved license silently
        print("🔄 Checking saved license...")
        is_valid, details = verify_license(SERVER_API_KEY, saved_license, PRODUCT_ID, API_URL)
        
        if is_valid:
            # License is valid, launch app directly (no heartbeat)
            print("✅ License verified! Launching application...")
            on_success_callback()
            return
        else:
            # Invalid/expired license, delete it and show window
            print(f"❌ Saved license invalid: {details.get('message', 'Unknown')}")
            delete_license()
    
    # No valid saved license, show activation window
    license_win = LicenseWindow(on_success_callback)
    license_win.run()
