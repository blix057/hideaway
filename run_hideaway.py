#!/usr/bin/env python3
"""
Hideaway Launcher - Main entry point for the app blocking system

Run this script to start the complete Hideaway system
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Add current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from hideaway_controller import HideawayController
    from setup_iphone import iPhoneSetup
    from supervised_profile_generator import SupervisedProfileGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files are in the same directory")
    sys.exit(1)

class HideawayLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hideaway - Setup & Launch")
        self.root.geometry("600x500")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Hideaway", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Remote iPhone App Blocker", font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Description
        desc_text = """Hideaway lets you remotely block distracting apps on your iPhone from your Mac.

Features:
• Block Instagram, YouTube, TikTok, and other apps
• One-click block/unblock toggle
• Works via WiFi using MDM
• Multiple focus modes (Study, Work, etc.)
• Blocks both apps and websites"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.grid(row=2, column=0, columnspan=2, pady=(0, 30), sticky=(tk.W, tk.E))
        
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
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(30, 0))
        
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
            except Exception as e:
                messagebox.showerror("Setup Error", f"iPhone setup failed: {str(e)}")
        
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
        """Generate pre-made focus profiles"""
        self.status_label.config(text="Generating profiles...")
        self.root.update()
        
        try:
            generator = SupervisedProfileGenerator()
            
            # Pre-defined focus modes
            focus_modes = {
                "Social Media Detox": [
                    "Instagram", "Facebook", "Twitter/X", "Snapchat", "TikTok", "Reddit"
                ],
                "Deep Work Mode": [
                    "Instagram", "YouTube", "TikTok", "Facebook", "Twitter/X", 
                    "Snapchat", "Reddit", "Netflix", "Spotify", "Discord"
                ],
                "Study Mode": [
                    "Instagram", "YouTube", "TikTok", "Netflix", "Discord", "Twitch"
                ]
            }
            
            profiles = generator.create_focus_profiles_set(focus_modes)
            
            # Save profiles
            saved_count = 0
            for mode_name, profile in profiles.items():
                filename = f"focus_mode_{mode_name.lower().replace(' ', '_')}.mobileconfig"
                generator.save_profile(profile, filename)
                saved_count += 1
                
            self.status_label.config(text=f"Generated {saved_count} profiles")
            messagebox.showinfo("Profiles Generated", f"Successfully created {saved_count} focus mode profiles!\n\nYou can now use these profiles with Hideaway.")
            
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate profiles: {str(e)}")
            self.status_label.config(text="Profile generation failed")
            
    def show_help(self):
        """Show help and instructions"""
        help_text = """🎯 Hideaway - Setup Guide

📱 STEP 1: iPhone Setup
1. Click "Setup iPhone" button
2. Wait for servers to start
3. Transfer the enrollment profile to your iPhone
4. Install the profile on your iPhone
5. Note your device ID from the logs

🎛️ STEP 2: Use Controller
1. Click "Launch Controller" button
2. Enter your device ID
3. Test connection
4. Select apps to block
5. Hit the BLOCK/UNBLOCK button

📋 STEP 3: Focus Profiles (Optional)
1. Click "Generate Profiles" to create pre-made blocking profiles
2. Use these profiles for different focus modes

⚠️ Important Notes:
• Your iPhone must be enrolled in MDM (supervised mode)
• You need Apple MDM push certificates for full functionality
• This works over WiFi between your Mac and iPhone
• Some restrictions require the device to be supervised

❓ Troubleshooting:
• Make sure both devices are on the same network
• Check that nanomdm server is running (port 9000)
• Verify your device ID is correct
• Try restarting the servers if connection fails"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Hideaway - Help")
        help_window.geometry("700x600")
        
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
    print("🎯 Hideaway - Starting...")
    
    # Check if we're in the right directory
    required_files = ['hideaway_controller.py', 'setup_iphone.py', 'supervised_profile_generator.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Make sure you're running this from the correct directory.")
        return
    
    launcher = HideawayLauncher()
    launcher.run()
    
if __name__ == "__main__":
    main()
