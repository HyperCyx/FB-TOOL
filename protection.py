"""
Advanced Anti-Debug and Protection System
Protects against license bypass attempts
"""

import sys
import os
import ctypes
import time
import psutil
import platform
import hashlib
import threading

class ProtectionSystem:
    """Advanced protection against debugging and tampering"""
    
    # Known debugger process names
    DEBUGGER_PROCESSES = [
        'x64dbg.exe', 'x32dbg.exe', 'windbg.exe', 'ollydbg.exe',
        'ida.exe', 'ida64.exe', 'idaq.exe', 'idaq64.exe',
        'devenv.exe', 'vsjitdebugger.exe', 'dnspy.exe',
        'scylla.exe', 'protection_id.exe', 'reshacker.exe',
        'importrec.exe', 'immunitydebugger.exe', 'wireshark.exe',
        'fiddler.exe', 'processhacker.exe', 'procmon.exe', 'procexp.exe',
        'cheatengine-x86_64.exe', 'cheatengine.exe'
    ]
    
    # Known VM artifacts
    VM_INDICATORS = [
        'vmware', 'virtualbox', 'vbox', 'qemu', 'xen',
        'parallels', 'virtual', 'vmtoolsd.exe', 'vmwaretray.exe'
    ]
    
    def __init__(self):
        self.running = True
        self.check_interval = 2  # Check every 2 seconds
        
    def check_debugger_attached(self):
        """Check if debugger is attached (Windows)"""
        if platform.system() == 'Windows':
            try:
                # IsDebuggerPresent API
                if ctypes.windll.kernel32.IsDebuggerPresent():
                    return True
                
                # CheckRemoteDebuggerPresent API
                debugger_present = ctypes.c_bool()
                ctypes.windll.kernel32.CheckRemoteDebuggerPresent(
                    ctypes.windll.kernel32.GetCurrentProcess(),
                    ctypes.byref(debugger_present)
                )
                if debugger_present.value:
                    return True
                    
            except:
                pass
        
        # Linux/Mac - check TracerPid in /proc/self/status
        elif platform.system() == 'Linux':
            try:
                with open('/proc/self/status') as f:
                    for line in f:
                        if line.startswith('TracerPid:'):
                            pid = int(line.split(':')[1].strip())
                            if pid != 0:
                                return True
            except:
                pass
        
        return False
    
    def check_debugger_processes(self):
        """Check for known debugger processes running"""
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    # Check both process name and executable path
                    proc_name = proc.info.get('name', '').lower()
                    proc_exe = proc.info.get('exe', '').lower()
                    
                    # Check process name
                    if any(dbg.lower() in proc_name for dbg in self.DEBUGGER_PROCESSES):
                        return True
                    
                    # Check executable path (catches renamed debuggers)
                    if proc_exe:
                        for dbg in self.DEBUGGER_PROCESSES:
                            if dbg.lower().replace('.exe', '') in proc_exe:
                                return True
                    
                    # Special check for x64dbg variants
                    if 'x64dbg' in proc_name or 'x32dbg' in proc_name or 'x96dbg' in proc_name:
                        return True
                    if proc_exe and ('x64dbg' in proc_exe or 'x32dbg' in proc_exe):
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        return False
    
    def check_vm_environment(self):
        """Detect if running in a virtual machine"""
        try:
            # Check system manufacturer/model
            if platform.system() == 'Windows':
                try:
                    import subprocess
                    result = subprocess.check_output(
                        'wmic computersystem get manufacturer,model',
                        shell=True, stderr=subprocess.DEVNULL
                    ).decode().lower()
                    
                    if any(vm in result for vm in self.VM_INDICATORS):
                        return True
                except:
                    pass
            
            # Check running processes for VM tools
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(vm in proc_name for vm in self.VM_INDICATORS):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except:
            pass
        return False
    
    def check_suspicious_parent(self):
        """Check if parent process is suspicious"""
        try:
            current_proc = psutil.Process(os.getpid())
            parent = current_proc.parent()
            
            if parent:
                parent_name = parent.name().lower()
                # Check if parent is a debugger
                if any(dbg.lower() in parent_name for dbg in self.DEBUGGER_PROCESSES):
                    return True
        except:
            pass
        return False
    
    def check_timing_attack(self):
        """Detect debugging via timing analysis"""
        try:
            start = time.perf_counter()
            # Simple operation that should be fast
            dummy = sum(range(1000))
            end = time.perf_counter()
            
            # If this takes too long, might be stepping through debugger
            if (end - start) > 0.01:  # 10ms threshold
                return True
        except:
            pass
        return False
    
    def verify_code_integrity(self):
        """Check if code has been modified"""
        try:
            # Get current script hash
            script_path = sys.argv[0]
            if os.path.exists(script_path):
                with open(script_path, 'rb') as f:
                    content = f.read()
                    current_hash = hashlib.sha256(content).hexdigest()
                    
                # Store expected hash (you should set this after deployment)
                # For now, just check if file is readable
                if len(current_hash) != 64:
                    return False
        except:
            return False
        return True
    
    def silent_exit(self):
        """Exit immediately when debugging detected"""
        try:
            # Show error message box on Windows
            if platform.system() == 'Windows':
                try:
                    import ctypes
                    ctypes.windll.user32.MessageBoxW(0, 
                        "Security Error: Debugging tools detected.\nApplication cannot run in this environment.", 
                        "Security Alert", 0x10)
                except:
                    pass
            else:
                # Linux/Mac: Print to stderr before exit
                print("\n❌ Security Error: Debugging tools detected.", file=sys.stderr)
                print("Application cannot run in this environment.\n", file=sys.stderr)
        except:
            pass
        
        # Force immediate exit
        os._exit(1)
    
    def continuous_check(self):
        """Continuously monitor for debugging attempts"""
        while self.running:
            try:
                # Run all checks
                if (self.check_debugger_attached() or
                    self.check_debugger_processes() or
                    self.check_suspicious_parent() or
                    self.check_timing_attack()):
                    # Detected - exit silently
                    self.silent_exit()
                
                # Sleep with random interval to avoid pattern detection
                import random
                time.sleep(self.check_interval + random.uniform(0, 1))
                
            except:
                # Any exception during check - exit silently
                self.silent_exit()
    
    def start_protection(self):
        """Start protection system in background"""
        # Initial check before starting
        if (self.check_debugger_attached() or
            self.check_debugger_processes() or
            self.check_vm_environment() or
            self.check_suspicious_parent()):
            self.silent_exit()
        
        # Start continuous monitoring in daemon thread
        monitor_thread = threading.Thread(
            target=self.continuous_check,
            daemon=True
        )
        monitor_thread.start()
    
    def stop_protection(self):
        """Stop protection monitoring"""
        self.running = False

# Global instance
_protection = None

def init_protection():
    """Initialize and start protection system"""
    global _protection
    _protection = ProtectionSystem()
    _protection.start_protection()
    return _protection

def verify_environment():
    """Quick verification before license check"""
    temp_protection = ProtectionSystem()
    
    # Quick checks
    if (temp_protection.check_debugger_attached() or
        temp_protection.check_debugger_processes() or
        temp_protection.check_vm_environment() or
        temp_protection.check_suspicious_parent()):
        temp_protection.silent_exit()
    
    return True
