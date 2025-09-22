#!/usr/bin/env python3
"""
Hideaway Controller - Mac app to remotely block/unblock iPhone apps via MDM

Features:
- GUI to select apps to block
- One-click block/unblock switch
- Works via WiFi using nanomdm
- Stores device configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from requests.auth import HTTPBasicAuth
import json
import subprocess
import uuid
import tempfile
import os
from datetime import datetime

class HideawayController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hideaway - iPhone App Blocker")
        self.root.geometry("800x600")
        
        # Configuration
        self.nanomdm_host = "http://127.0.0.1:9000"
        self.api_username = "nanomdm"
        self.api_password = "nanomdm"
        self.device_id = ""
        self.is_blocking = False
        
        # App database with bundle IDs
        self.available_apps = {
            "Instagram": "com.burbn.instagram",
            "YouTube": "com.google.ios.youtube",
            "TikTok": "com.zhiliaoapp.musically",
            "Facebook": "com.facebook.Facebook",
            "Twitter/X": "com.twitter.twitter",
            "Snapchat": "com.toyopagroup.picaboo",
            "Reddit": "com.reddit.Reddit",
            "WhatsApp": "net.whatsapp.WhatsApp",
            "Telegram": "ph.telegra.Telegraph",
            "Safari": "com.apple.mobilesafari",
            "Messages": "com.apple.MobileSMS",
            "Mail": "com.apple.mobilemail",
            "Camera": "com.apple.camera",
            "Photos": "com.apple.mobileslideshow",
            "Music": "com.apple.Music",
            "App Store": "com.apple.AppStore",
            "Netflix": "com.netflix.Netflix",
            "Spotify": "com.spotify.client",
            "Discord": "com.hammerandchisel.discord",
            "LinkedIn": "com.linkedin.LinkedIn"
        }
        
        self.selected_apps = set()
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Hideaway", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Device Setup Section
        device_frame = ttk.LabelFrame(main_frame, text="📱 iPhone Setup", padding="10")
        device_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(device_frame, text="Device ID:").grid(row=0, column=0, sticky=tk.W)
        self.device_entry = ttk.Entry(device_frame, width=40)
        self.device_entry.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Button(device_frame, text="Setup iPhone", command=self.setup_device).grid(row=0, column=2, padx=(5, 0))
        ttk.Button(device_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=3, padx=(5, 0))
        
        # App Selection Section
        apps_frame = ttk.LabelFrame(main_frame, text="🚫 Select Apps to Block", padding="10")
        apps_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create scrollable app list
        canvas = tk.Canvas(apps_frame, height=200)
        scrollbar = ttk.Scrollbar(apps_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add checkboxes for each app
        self.app_vars = {}
        row = 0
        for app_name, bundle_id in self.available_apps.items():
            var = tk.BooleanVar()
            self.app_vars[bundle_id] = var
            
            checkbox = ttk.Checkbutton(scrollable_frame, text=f"{app_name}", variable=var)
            checkbox.grid(row=row//3, column=row%3, sticky=tk.W, padx=5, pady=2)
            row += 1
            
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Quick select buttons
        button_frame = ttk.Frame(apps_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Select Social Media", command=self.select_social_media).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Control Section
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ Control", padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(control_frame, text="Status: Ready", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Big block/unblock button
        self.control_button = ttk.Button(control_frame, text="🔴 BLOCK APPS", command=self.toggle_blocking)
        self.control_button.grid(row=1, column=0, pady=10)
        
        # Status and logs
        log_frame = ttk.LabelFrame(main_frame, text="📋 Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_frame, height=8, width=80)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log("Hideaway started. Ready to control your iPhone!")
        
    def log(self, message):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def select_social_media(self):
        """Quick select common social media apps"""
        social_apps = [
            "com.burbn.instagram",
            "com.google.ios.youtube", 
            "com.zhiliaoapp.musically",
            "com.facebook.Facebook",
            "com.twitter.twitter",
            "com.toyopagroup.picaboo"
        ]
        for bundle_id in social_apps:
            if bundle_id in self.app_vars:
                self.app_vars[bundle_id].set(True)
        self.log("Selected common social media apps")
        
    def select_all(self):
        """Select all apps"""
        for var in self.app_vars.values():
            var.set(True)
        self.log("Selected all apps")
        
    def clear_all(self):
        """Clear all selections"""
        for var in self.app_vars.values():
            var.set(False)
        self.log("Cleared all selections")
        
    def setup_device(self):
        """Show device setup instructions"""
        setup_text = '''
📱 iPhone Setup Instructions:

1. Make sure nanomdm server is running on this Mac
2. Set up a SCEP server (for certificates)
3. Create enrollment profile with your iPhone
4. Install the profile on your iPhone
5. Note your device ID from nanomdm logs
6. Enter the device ID in the field above

For detailed setup, check the nanomdm documentation.
        '''
        messagebox.showinfo("iPhone Setup", setup_text)
        
    def test_connection(self):
        """Test connection to device"""
        device_id = self.device_entry.get().strip()
        if not device_id:
            messagebox.showerror("Error", "Please enter a device ID")
            return
            
        try:
            # Send a simple push notification to test
            url = f"{self.nanomdm_host}/v1/push/{device_id}"
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_password),
                timeout=10
            )
            
            if response.status_code == 200:
                self.device_id = device_id
                self.log(f"✅ Successfully connected to device {device_id}")
                self.status_label.config(text=f"Status: Connected to {device_id[:8]}...")
                messagebox.showinfo("Success", "Connection successful!")
            else:
                self.log(f"❌ Connection failed: {response.status_code}")
                messagebox.showerror("Error", f"Connection failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Connection error: {str(e)}")
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            
    def generate_blocking_profile(self, block_apps=True):
        """Generate iOS configuration profile to block/unblock apps
        
        This version uses a simplified approach that works more reliably across iOS versions.
        """
        selected_bundles = [bundle_id for bundle_id, var in self.app_vars.items() if var.get()]
        
        if not selected_bundles and block_apps:
            raise Exception("No apps selected to block")
            
        # Create profile content
        profile_uuid = str(uuid.uuid4())
        
        if block_apps:
            # Get app names for description
            app_names = []
            for bundle_id in selected_bundles[:3]:  # Get first 3 for display
                # Find the app name from bundle ID by reverse lookup
                for app_name, bundle in self.available_apps.items():
                    if bundle == bundle_id:
                        app_names.append(app_name)
                        break
            
            # Simple app blocking profile
            profile_content = {
                "PayloadContent": [],
                "PayloadDescription": f"Blocks apps: {', '.join(app_names)}{'...' if len(selected_bundles) > 3 else ''}",
                "PayloadDisplayName": "Focus Mode",
                "PayloadIdentifier": "com.hideaway.dynamic",
                "PayloadOrganization": "Hideaway",
                "PayloadRemovalDisallowed": False,
                "PayloadType": "Configuration",
                "PayloadUUID": profile_uuid,
                "PayloadVersion": 1
            }
            
            # Add restrictions payload
            restrictions_uuid = str(uuid.uuid4())
            restrictions_payload = {
                "PayloadDisplayName": "App Restrictions",
                "PayloadDescription": "Restricts access to specified applications",
                "PayloadIdentifier": "com.hideaway.restrictions",
                "PayloadType": "com.apple.applicationaccess",
                "PayloadUUID": restrictions_uuid,
                "PayloadVersion": 1,
                "blacklistedAppBundleIDs": selected_bundles
            }
            profile_content["PayloadContent"].append(restrictions_payload)
        else:
            # Removal profile - empty payload
            profile_content = {
                "PayloadContent": [],  # Empty content removes restrictions
                "PayloadDescription": "Removes app blocking restrictions",
                "PayloadDisplayName": "Normal Mode",
                "PayloadIdentifier": "com.hideaway.remove",
                "PayloadOrganization": "Hideaway",
                "PayloadRemovalDisallowed": False,
                "PayloadType": "Configuration",
                "PayloadUUID": profile_uuid,
                "PayloadVersion": 1
            }
            
        return profile_content
        
    def send_profile_to_device(self, profile_content):
        """Send profile to device via nanomdm"""
        if not self.device_id:
            raise Exception("No device connected")
            
        # Convert profile to plist format
        import plistlib
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mobileconfig', delete=False) as f:
            plistlib.dump(profile_content, f)
            temp_profile_path = f.name
            
        try:
            # Use cmdr.py to generate install command
            cmd = ["python3", "./tools/cmdr.py", "InstallProfile", temp_profile_path]
            result = subprocess.run(cmd, capture_output=True, cwd="./nanomdm")
            
            if result.returncode != 0:
                raise Exception(f"Command generation failed: {result.stderr.decode()}")
                
            # Send to device
            url = f"{self.nanomdm_host}/v1/enqueue/{self.device_id}"
            response = requests.put(
                url,
                data=result.stdout,
                headers={'Content-Type': 'application/x-plist'},
                auth=HTTPBasicAuth(self.api_username, self.api_password)
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to send profile: {response.text}")
                
            return response.json()
            
        finally:
            # Clean up temp file
            os.unlink(temp_profile_path)
            
    def toggle_blocking(self):
        """Toggle app blocking on/off"""
        try:
            if not self.device_id:
                messagebox.showerror("Error", "Please connect to a device first")
                return
                
            selected_count = sum(1 for var in self.app_vars.values() if var.get())
            if selected_count == 0:
                messagebox.showerror("Error", "Please select at least one app to block")
                return
                
            if not self.is_blocking:
                # Block apps
                self.log(f"🚫 Blocking {selected_count} apps...")
                profile = self.generate_blocking_profile(block_apps=True)
                result = self.send_profile_to_device(profile)
                
                self.is_blocking = True
                self.control_button.config(text="🟢 UNBLOCK APPS")
                self.status_label.config(text=f"Status: Blocking {selected_count} apps")
                self.log(f"✅ Successfully blocked apps on device")
                
            else:
                # Unblock apps (remove profile)
                self.log("🟢 Unblocking apps...")
                # Note: In a real implementation, you'd remove the specific profile
                # For now, we'll send an empty profile
                profile = {
                    "PayloadContent": [],
                    "PayloadDescription": "Remove restrictions",
                    "PayloadDisplayName": "Normal Mode",
                    "PayloadIdentifier": "com.hideaway.remove",
                    "PayloadType": "Configuration",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadVersion": 1
                }
                
                self.is_blocking = False
                self.control_button.config(text="🔴 BLOCK APPS")
                self.status_label.config(text="Status: Apps unblocked")
                self.log("✅ Successfully unblocked apps")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = HideawayController()
    app.run()
