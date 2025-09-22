#!/usr/bin/env python3
"""
Hideaway - Remote iPhone App Blocker (NanoMDM Compatible Version)

Fixed to work properly with nanomdm and iOS MDM based on official examples.
All functionality bundled into a single file for easy distribution.
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from requests.auth import HTTPBasicAuth
import json
import uuid
import tempfile
import threading
import time
import plistlib
from datetime import datetime, timedelta
import platform

# Get user's home directory and Desktop path
HOME_DIR = os.path.expanduser("~")
DESKTOP_DIR = os.path.join(HOME_DIR, "Desktop")

class SupervisedProfileGenerator:
    """Profile generator compatible with nanomdm and iOS MDM standards"""
    
    def __init__(self):
        # Comprehensive app bundle database
        self.app_bundles = {
            # Social Media
            "Instagram": "com.burbn.instagram",
            "YouTube": "com.google.ios.youtube", 
            "TikTok": "com.zhiliaoapp.musically",
            "Facebook": "com.facebook.Facebook",
            "Twitter/X": "com.twitter.twitter",
            "Snapchat": "com.toyopagroup.picaboo",
            "Reddit": "com.reddit.Reddit",
            "Discord": "com.hammerandchisel.discord",
            "LinkedIn": "com.linkedin.LinkedIn",
            "Pinterest": "com.pinterest.pinterest",
            
            # Entertainment
            "Netflix": "com.netflix.Netflix",
            "Disney+": "com.disney.disneyplus",
            "Amazon Prime": "com.amazon.avod.thirdpartyclient",
            "Spotify": "com.spotify.client",
            "Twitch": "tv.twitch",
            
            # Games (examples)
            "Candy Crush": "com.king.candycrushsaga",
            "PUBG Mobile": "com.tencent.ig",
            "Clash of Clans": "com.supercell.magic",
            
            # Apple Apps (these can be blocked on supervised devices)
            "Safari": "com.apple.mobilesafari",
            "Camera": "com.apple.camera", 
            "Photos": "com.apple.mobileslideshow",
            "Music": "com.apple.Music",
            "App Store": "com.apple.AppStore",
            "iTunes Store": "com.apple.MobileStore",
            "Messages": "com.apple.MobileSMS",
            "Mail": "com.apple.mobilemail",
            "FaceTime": "com.apple.facetime",
            "Maps": "com.apple.Maps",
            "News": "com.apple.news",
            
            # Messaging
            "WhatsApp": "net.whatsapp.WhatsApp",
            "Telegram": "ph.telegra.Telegraph",
            "Signal": "org.whispersystems.signal",
            "Messenger": "com.facebook.Messenger"
        }
        
    def create_app_blocking_profile(self, blocked_apps, profile_name="Focus Mode"):
        """Create iOS-compatible configuration profile using proper MDM structures"""
        
        profile_uuid = str(uuid.uuid4()).upper()
        restrictions_uuid = str(uuid.uuid4()).upper()
        
        # Use the exact structure from Apple's Configuration Profile Reference
        profile = {
            "PayloadContent": [],
            "PayloadDescription": f"Blocks selected apps: {', '.join(blocked_apps[:3])}{'...' if len(blocked_apps) > 3 else ''}",
            "PayloadDisplayName": profile_name,
            "PayloadIdentifier": f"com.hideaway.appblock.{profile_uuid.lower()}",
            "PayloadOrganization": "Hideaway",
            "PayloadRemovalDisallowed": False,
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        # Create restrictions payload using Apple's exact specification
        # This is based on Apple's Configuration Profile Reference
        restrictions_payload = {
            "PayloadDisplayName": "App Restrictions",
            "PayloadDescription": "Restricts access to specified applications",
            "PayloadIdentifier": f"com.hideaway.restrictions.{restrictions_uuid.lower()}",
            "PayloadType": "com.apple.applicationaccess",
            "PayloadUUID": restrictions_uuid,
            "PayloadVersion": 1,
            
            # Use the correct key name from Apple's documentation
            "familyControlsEnabled": False,
            "blacklistedAppBundleIDs": blocked_apps,
        }
        
        profile["PayloadContent"].append(restrictions_payload)
        
        return profile
    
    def create_focus_profiles_set(self, focus_modes):
        """Create multiple focus profiles for different scenarios"""
        profiles = {}
        
        for mode_name, app_names in focus_modes.items():
            # Convert app names to bundle IDs
            bundle_ids = []
            for app_name in app_names:
                if app_name in self.app_bundles:
                    bundle_ids.append(self.app_bundles[app_name])
            
            # Create profile for this focus mode
            if bundle_ids:
                profiles[mode_name] = self.create_app_blocking_profile(
                    bundle_ids, 
                    f"Hideaway {mode_name}"
                )
                
        return profiles
    
    def save_profile(self, profile, filename):
        """Save profile to Desktop for easy access"""
        filepath = os.path.join(DESKTOP_DIR, filename)
        
        with open(filepath, 'wb') as f:
            plistlib.dump(profile, f)
        
        return filepath

class iPhoneSetup:
    """iPhone setup using proper nanomdm enrollment profile structure"""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.join(HOME_DIR, "hideaway_setup")
        
        self.base_dir = base_dir
        self.nanomdm_dir = f"{base_dir}/nanomdm"
        self.certs_dir = f"{base_dir}/certs"
        self.scep_dir = f"{base_dir}/scep"
        
        # Server configuration
        self.nanomdm_port = 9000
        self.scep_port = 8080
        self.api_key = "hideaway"
        
        # URLs (these would be replaced with actual server URLs in production)
        self.nanomdm_url = "https://your-mdm-server.com"  # Replace with actual server
        self.scep_url = "https://your-scep-server.com"    # Replace with actual server
        
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories"""
        for directory in [self.base_dir, self.certs_dir, self.scep_dir, self.nanomdm_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def create_enrollment_profile(self, device_name="iPhone"):
        """Create nanomdm-compatible iPhone enrollment profile"""
        print("📱 Creating nanomdm-compatible enrollment profile...")
        
        # Generate UUIDs for each payload - use uppercase as per Apple standards
        profile_uuid = str(uuid.uuid4()).upper()
        scep_uuid = str(uuid.uuid4()).upper() 
        mdm_uuid = str(uuid.uuid4()).upper()
        
        # Create SCEP payload using exact structure from nanomdm example
        scep_payload = {
            "PayloadContent": {
                "URL": f"{self.scep_url}/scep",
                "Challenge": "hideaway", 
                "Key Type": "RSA",
                "Key Usage": 5,
                "Keysize": 2048
            },
            "PayloadIdentifier": "com.hideaway.scep",
            "PayloadType": "com.apple.security.scep",
            "PayloadUUID": scep_uuid,
            "PayloadVersion": 1
        }
        
        # Create MDM payload using exact structure from nanomdm example  
        mdm_payload = {
            "AccessRights": 8191,  # All MDM rights
            "CheckOutWhenRemoved": True,
            "IdentityCertificateUUID": scep_uuid,  # Reference to SCEP certificate
            "PayloadIdentifier": "com.hideaway.mdm",
            "PayloadType": "com.apple.mdm",
            "PayloadUUID": mdm_uuid,
            "PayloadVersion": 1,
            "ServerCapabilities": [
                "com.apple.mdm.per-user-connections",
                "com.apple.mdm.bootstraptoken",
                "com.apple.mdm.token"
            ],
            "ServerURL": f"{self.nanomdm_url}/mdm",
            "SignMessage": True,
            "Topic": "com.apple.mgmt.External.hideaway-push-topic"  # Replace with actual push topic
        }
        
        # Main enrollment profile using exact structure from nanomdm
        profile = {
            "PayloadContent": [scep_payload, mdm_payload],
            "PayloadDisplayName": f"Hideaway Enrollment - {device_name}",
            "PayloadIdentifier": "com.hideaway.enrollment", 
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        # Save to Desktop
        filename = "Hideaway_Enrollment_NanoMDM.mobileconfig"
        filepath = os.path.join(DESKTOP_DIR, filename)
        
        with open(filepath, 'wb') as f:
            plistlib.dump(profile, f)
        
        print(f"✅ nanomdm-compatible enrollment profile saved to Desktop: {filename}")
        print("📋 This profile uses the exact structure from nanomdm examples")
        print("⚠️  Note: You need to replace the server URLs and push topic with your actual values")
        print("📖 See nanomdm documentation for setup: https://github.com/micromdm/nanomdm")
        
        return filepath

    def run_full_setup(self):
        """Run the complete iPhone setup process"""
        print("🎯 Starting Hideaway iPhone Setup (nanomdm compatible)...")
        
        # Create enrollment profile on Desktop
        profile_path = self.create_enrollment_profile()
        
        print("\n✅ Setup completed!")
        print(f"📱 Enrollment profile saved to: {os.path.basename(profile_path)}")
        print("💡 You can now find the enrollment profile on your Desktop")
        print("\n🔧 Next steps:")
        print("1. Set up your nanomdm server (see nanomdm docs)")
        print("2. Replace server URLs in the enrollment profile")
        print("3. Add your actual push certificate topic")
        print("4. Install the profile on your iPhone")

class HideawayController:
    """Main Hideaway controller application using nanomdm-compatible profiles"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hideaway - iPhone App Blocker (nanomdm Compatible)")
        self.root.geometry("800x600")
        
        # Configuration
        self.nanomdm_host = "http://127.0.0.1:9000"
        self.api_username = "nanomdm" 
        self.api_password = "nanomdm"
        self.device_id = ""
        self.is_blocking = False
        
        # Initialize profile generator
        self.profile_generator = SupervisedProfileGenerator()
        
        # App database with bundle IDs
        self.available_apps = self.profile_generator.app_bundles
        
        self.selected_apps = set()
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Hideaway (nanomdm)", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Device Setup Section
        device_frame = ttk.LabelFrame(main_frame, text="📱 iPhone Setup", padding="10")
        device_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(device_frame, text="Device UDID:").grid(row=0, column=0, sticky=tk.W)
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
        
        self.log("Hideaway (nanomdm compatible) started!")
        self.log("📖 This version uses profiles compatible with nanomdm and iOS MDM standards")
        self.log("⚠️  Make sure your nanomdm server is properly configured")
        
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
        """Launch iPhone setup process"""
        self.log("Starting iPhone setup...")
        
        def run_setup():
            try:
                setup = iPhoneSetup()
                setup.run_full_setup()
                self.log("✅ iPhone setup completed! Check your Desktop for the enrollment profile.")
            except Exception as e:
                self.log(f"❌ Setup failed: {str(e)}")
                messagebox.showerror("Setup Error", f"iPhone setup failed: {str(e)}")
        
        # Run setup in separate thread to avoid blocking UI
        thread = threading.Thread(target=run_setup)
        thread.daemon = True
        thread.start()
        
    def test_connection(self):
        """Test connection to nanomdm server"""
        device_id = self.device_entry.get().strip()
        if not device_id:
            # If no device ID provided, just simulate connection for demo
            self.device_id = "demo_device"
            self.log("✅ Demo mode - profiles will be saved to Desktop")
            self.status_label.config(text="Status: Demo mode active")
            messagebox.showinfo("Demo Mode", "No device UDID provided. Running in demo mode - profiles will be saved to Desktop.")
            return
        
        # Try to connect to nanomdm server
        try:
            # Test nanomdm API endpoint
            url = f"{self.nanomdm_host}/v1/push/{device_id}"
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_password),
                timeout=10
            )
            
            if response.status_code == 200:
                self.device_id = device_id
                self.log(f"✅ Connected to nanomdm server for device {device_id}")
                self.status_label.config(text=f"Status: Connected to {device_id[:8]}...")
                messagebox.showinfo("Success", "Connection to nanomdm server successful!")
            else:
                self.log(f"❌ nanomdm server connection failed: {response.status_code}")
                # Fall back to demo mode
                self.device_id = "demo_device"
                self.status_label.config(text="Status: Demo mode (server not available)")
                messagebox.showwarning("Server Unavailable", f"Could not connect to nanomdm server.\nUsing demo mode - profiles will be saved to Desktop.")
                
        except Exception as e:
            self.log(f"❌ Connection error: {str(e)}")
            # Fall back to demo mode
            self.device_id = "demo_device" 
            self.status_label.config(text="Status: Demo mode (server unavailable)")
            messagebox.showwarning("Connection Error", f"Could not connect to nanomdm server: {str(e)}\n\nUsing demo mode - profiles will be saved to Desktop.")
            
    def generate_blocking_profile(self, block_apps=True):
        """Generate nanomdm-compatible iOS configuration profile"""
        selected_bundles = [bundle_id for bundle_id, var in self.app_vars.items() if var.get()]
        
        if not selected_bundles and block_apps:
            raise Exception("No apps selected to block")
        
        if block_apps:
            # Get app names for description
            app_names = []
            for bundle_id in selected_bundles[:3]:  # Get first 3 for display
                # Find the app name from bundle ID by reverse lookup
                for app_name, bundle in self.available_apps.items():
                    if bundle == bundle_id:
                        app_names.append(app_name)
                        break
            
            profile = self.profile_generator.create_app_blocking_profile(
                selected_bundles, 
                f"Hideaway Block - {', '.join(app_names)}"[:50]
            )
        else:
            # Simple removal profile - just empty payload
            profile = {
                "PayloadContent": [],
                "PayloadDescription": "Removes app blocking restrictions",
                "PayloadDisplayName": "Hideaway Unblock",
                "PayloadIdentifier": f"com.hideaway.remove.{str(uuid.uuid4()).lower()}",
                "PayloadOrganization": "Hideaway",
                "PayloadRemovalDisallowed": False,
                "PayloadType": "Configuration",
                "PayloadUUID": str(uuid.uuid4()).upper(),
                "PayloadVersion": 1
            }
            
        return profile
        
    def send_profile_to_device(self, profile_content):
        """Send profile to device via nanomdm or save to Desktop"""
        if not self.device_id:
            raise Exception("No device connected")
        
        # Save profile to Desktop with timestamp
        filename = f"hideaway_nanomdm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mobileconfig"
        filepath = os.path.join(DESKTOP_DIR, filename)
        
        with open(filepath, 'wb') as f:
            plistlib.dump(profile_content, f)
            
        self.log(f"📁 Profile saved to Desktop: {filename}")
        
        # If we have a real device connection, also try to send via nanomdm
        if self.device_id != "demo_device":
            try:
                # Use nanomdm's cmdr.py approach - send InstallProfile command
                # This requires nanomdm tools to be available
                cmdr_path = os.path.join(os.path.dirname(__file__), "nanomdm", "tools", "cmdr.py")
                if os.path.exists(cmdr_path):
                    # Generate InstallProfile command using cmdr.py
                    cmd = ["python3", cmdr_path, "InstallProfile", filepath]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Send command to nanomdm
                        url = f"{self.nanomdm_host}/v1/enqueue/{self.device_id}"
                        response = requests.put(
                            url,
                            data=result.stdout.encode(),
                            headers={'Content-Type': 'application/x-plist'},
                            auth=HTTPBasicAuth(self.api_username, self.api_password)
                        )
                        
                        if response.status_code == 200:
                            self.log("📡 Profile sent to device via nanomdm!")
                            return {"status": "sent_via_nanomdm", "filepath": filepath}
                        else:
                            self.log(f"⚠️ nanomdm send failed: {response.status_code}")
                    else:
                        self.log(f"⚠️ Command generation failed: {result.stderr}")
                else:
                    self.log("⚠️ nanomdm tools not found - profile saved to Desktop only")
            except Exception as e:
                self.log(f"⚠️ nanomdm send error: {str(e)}")
        
        self.log("📱 Transfer this profile to your iPhone and install it manually")
        return {"status": "saved_to_desktop", "filepath": filepath}
            
    def toggle_blocking(self):
        """Toggle app blocking on/off"""
        try:
            selected_count = sum(1 for var in self.app_vars.values() if var.get())
            if selected_count == 0:
                messagebox.showerror("Error", "Please select at least one app to block")
                return
                
            if not self.is_blocking:
                # Block apps
                self.log(f"🚫 Creating blocking profile for {selected_count} apps...")
                profile = self.generate_blocking_profile(block_apps=True)
                result = self.send_profile_to_device(profile)
                
                self.is_blocking = True
                self.control_button.config(text="🟢 UNBLOCK APPS")
                self.status_label.config(text=f"Status: Blocking {selected_count} apps")
                self.log(f"✅ Blocking profile created successfully")
                
                if result["status"] == "sent_via_nanomdm":
                    messagebox.showinfo("Profile Sent", f"Blocking profile sent to device via nanomdm!\n\nIt should install automatically on your iPhone.")
                else:
                    messagebox.showinfo("Profile Created", f"Blocking profile saved to Desktop!\n\nTransfer it to your iPhone and install to block {selected_count} apps.")
                
            else:
                # Unblock apps (remove profile)
                self.log("🟢 Creating unblock profile...")
                profile = self.generate_blocking_profile(block_apps=False)
                result = self.send_profile_to_device(profile)
                
                self.is_blocking = False
                self.control_button.config(text="🔴 BLOCK APPS")
                self.status_label.config(text="Status: Apps unblocked")
                self.log("✅ Unblock profile created successfully")
                
                if result["status"] == "sent_via_nanomdm":
                    messagebox.showinfo("Profile Sent", "Unblock profile sent to device via nanomdm!")
                else:
                    messagebox.showinfo("Profile Created", "Unblock profile saved to Desktop!\n\nTransfer it to your iPhone and install to remove app restrictions.")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

class HideawayLauncher:
    """Main launcher interface for Hideaway (nanomdm Compatible)"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hideaway - Setup & Launch (nanomdm Compatible)")
        self.root.geometry("600x550")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Hideaway (nanomdm)", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Remote iPhone App Blocker", font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Description
        desc_text = """Hideaway lets you remotely block distracting apps on your iPhone from your Mac.

nanomdm Compatible Version:
• Uses proper MDM profile structures from nanomdm examples
• Compatible with Apple's Configuration Profile standards
• Works with nanomdm server infrastructure
• All profiles saved to Desktop for easy access
• Supports automatic profile deployment via nanomdm API"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        setup_btn = ttk.Button(button_frame, text="📱 Setup iPhone", command=self.setup_iphone, width=20)
        setup_btn.grid(row=0, column=0, padx=10, pady=5)
        
        launch_btn = ttk.Button(button_frame, text="🎛️ Launch Hideaway", command=self.launch_controller, width=20)
        launch_btn.grid(row=0, column=1, padx=10, pady=5)
        
        profiles_btn = ttk.Button(button_frame, text="📋 Generate Profiles", command=self.generate_profiles, width=20)
        profiles_btn.grid(row=1, column=0, padx=10, pady=5)
        
        help_btn = ttk.Button(button_frame, text="❓ Help & Instructions", command=self.show_help, width=20)
        help_btn.grid(row=1, column=1, padx=10, pady=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready to start", font=("Arial", 10))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def setup_iphone(self):
        """Launch iPhone setup process"""
        self.status_label.config(text="Setting up iPhone...")
        self.root.update()
        
        def run_setup():
            try:
                setup = iPhoneSetup()
                setup.run_full_setup()
                self.status_label.config(text="Setup completed! Check Desktop for nanomdm enrollment profile.")
            except Exception as e:
                messagebox.showerror("Setup Error", f"iPhone setup failed: {str(e)}")
                self.status_label.config(text="Setup failed")
        
        # Run setup in separate thread to avoid blocking UI
        thread = threading.Thread(target=run_setup)
        thread.daemon = True
        thread.start()
        
    def launch_controller(self):
        """Launch the main Hideaway app"""
        self.status_label.config(text="Launching Hideaway...")
        self.root.update()
        
        try:
            self.root.withdraw()  # Hide launcher window
            app = HideawayController()
            app.run()
            self.root.deiconify()  # Show launcher window again when controller closes
            self.status_label.config(text="Hideaway closed")
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Launch Error", f"Failed to launch Hideaway: {str(e)}")
            self.status_label.config(text="Launch failed")
            
    def generate_profiles(self):
        """Generate pre-made focus profiles using nanomdm-compatible structure"""
        self.status_label.config(text="Generating nanomdm-compatible profiles...")
        self.root.update()
        
        try:
            generator = SupervisedProfileGenerator()
            
            # Pre-defined focus modes (simplified for better compatibility)
            focus_modes = {
                "Social Media Detox": [
                    "Instagram", "Facebook", "Twitter/X", "Snapchat", "TikTok", "Reddit"
                ],
                "Study Mode": [
                    "Instagram", "YouTube", "TikTok", "Netflix", "Discord"
                ],
                "Work Mode": [
                    "Instagram", "TikTok", "Facebook", "Twitter/X", "YouTube"
                ]
            }
            
            profiles = generator.create_focus_profiles_set(focus_modes)
            
            # Save profiles to Desktop
            saved_count = 0
            for mode_name, profile in profiles.items():
                filename = f"hideaway_nanomdm_{mode_name.lower().replace(' ', '_')}.mobileconfig"
                generator.save_profile(profile, filename)
                saved_count += 1
                
            self.status_label.config(text=f"Generated {saved_count} nanomdm profiles on Desktop")
            messagebox.showinfo("Profiles Generated", f"Successfully created {saved_count} nanomdm-compatible focus mode profiles on your Desktop!\n\nThese use the proper MDM structure and should work reliably with iOS.")
            
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate profiles: {str(e)}")
            self.status_label.config(text="Profile generation failed")
            
    def show_help(self):
        """Show help and instructions"""
        help_text = """🎯 Hideaway (nanomdm Compatible) - Setup Guide

🔧 What's Different:
• Uses exact MDM profile structures from nanomdm examples  
• Compatible with Apple's Configuration Profile Reference
• Proper SCEP and MDM payload structures
• Works with nanomdm server infrastructure

📖 Prerequisites:
1. nanomdm server properly set up and running
2. SCEP server configured and accessible
3. Valid Apple Push Certificate installed in nanomdm
4. iPhone enrolled in your MDM system

📱 STEP 1: Setup nanomdm Server
1. Follow nanomdm quickstart guide
2. Set up SCEP server with proper certificates
3. Configure nanomdm with your push certificate
4. Ensure both servers are accessible

🎛️ STEP 2: iPhone Setup
1. Click "Setup iPhone" to generate enrollment profile
2. Replace placeholder URLs with your actual server addresses
3. Transfer profile to iPhone and install
4. Note the device UDID for use in the controller

📋 STEP 3: Use Controller
1. Click "Launch Hideaway" 
2. Enter device UDID
3. Select apps to block
4. Profiles will be sent via nanomdm API (if available) or saved to Desktop

🔗 References:
• nanomdm docs: https://github.com/micromdm/nanomdm
• Apple Configuration Profile Reference
• MDM Protocol documentation

📁 All profiles use standard MDM structures and are saved to Desktop!"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Hideaway (nanomdm) - Help")
        help_window.geometry("800x700")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")  # Make read-only
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def run(self):
        """Start the launcher"""
        self.root.mainloop()

def main():
    print("🎯 Hideaway (nanomdm Compatible) - Starting...")
    print("📖 This version uses proper MDM structures from nanomdm examples")
    print("🔧 Make sure your nanomdm server is properly configured")
    
    # Create Desktop directory if it doesn't exist
    os.makedirs(DESKTOP_DIR, exist_ok=True)
    
    launcher = HideawayLauncher()
    launcher.run()

if __name__ == "__main__":
    main()