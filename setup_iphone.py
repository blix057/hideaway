#!/usr/bin/env python3
"""
iPhone Setup Automation - Simplifies the process of enrolling iPhone in nanomdm

This script automates as much as possible of the iPhone enrollment process
"""

import os
import subprocess
import requests
import uuid
import plistlib
from datetime import datetime, timedelta
import json

class iPhoneSetup:
    def __init__(self, base_dir="/Users/paul/Files/vsc_projekte/app_block"):
        self.base_dir = base_dir
        self.nanomdm_dir = f"{base_dir}/nanomdm"
        self.certs_dir = f"{base_dir}/certs"
        self.scep_dir = f"{base_dir}/scep"
        
        # Server configuration
        self.nanomdm_port = 9000
        self.scep_port = 8080
        self.api_key = "nanomdm"
        
        # URLs (will be updated when ngrok starts)
        self.nanomdm_url = f"http://127.0.0.1:{self.nanomdm_port}"
        self.scep_url = f"http://127.0.0.1:{self.scep_port}"
        self.public_nanomdm_url = ""
        self.public_scep_url = ""
        
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories"""
        for directory in [self.certs_dir, self.scep_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def check_requirements(self):
        """Check if all requirements are installed"""
        requirements = {
            "python3": "python3 --version",
            "go": "go version",
            "curl": "curl --version",
            "openssl": "openssl version"
        }
        
        print("🔍 Checking requirements...")
        missing = []
        
        for tool, cmd in requirements.items():
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {tool}: OK")
                else:
                    print(f"  ❌ {tool}: Not found")
                    missing.append(tool)
            except FileNotFoundError:
                print(f"  ❌ {tool}: Not found")
                missing.append(tool)
                
        if missing:
            print(f"\n❌ Missing requirements: {', '.join(missing)}")
            print("Please install missing tools before continuing.")
            return False
            
        return True
        
    def setup_scep_server(self):
        """Download and setup SCEP server"""
        print("🔧 Setting up SCEP server...")
        
        # Check if already downloaded
        scep_binary = f"{self.scep_dir}/scepserver"
        if os.path.exists(scep_binary):
            print("  ✅ SCEP server already available")
            return True
            
        # Download SCEP server
        import platform
        system = platform.system().lower()
        arch = "arm64" if platform.machine() == "arm64" else "amd64"
        
        scep_url = f"https://github.com/micromdm/scep/releases/download/v2.1.0/scepserver-{system}-{arch}-v2.1.0.zip"
        
        print(f"  📥 Downloading SCEP server from {scep_url}...")
        
        try:
            # Download
            subprocess.run([
                "curl", "-RLO", scep_url
            ], cwd=self.scep_dir, check=True)
            
            # Extract
            zip_file = f"scepserver-{system}-{arch}-v2.1.0.zip"
            subprocess.run([
                "unzip", zip_file
            ], cwd=self.scep_dir, check=True)
            
            # Rename to generic name
            original_name = f"scepserver-{system}-{arch}"
            os.rename(f"{self.scep_dir}/{original_name}", scep_binary)
            
            # Make executable
            os.chmod(scep_binary, 0o755)
            
            # Initialize CA
            subprocess.run([
                scep_binary, "ca", "-init"
            ], cwd=self.scep_dir, check=True)
            
            print("  ✅ SCEP server setup complete")
            return True
            
        except Exception as e:
            print(f"  ❌ SCEP setup failed: {e}")
            return False
            
    def start_scep_server(self):
        """Start SCEP server in background"""
        print("🚀 Starting SCEP server...")
        
        scep_binary = f"{self.scep_dir}/scepserver"
        
        try:
            # Start SCEP server
            process = subprocess.Popen([
                scep_binary,
                "-allowrenew", "0",
                "-challenge", "focuscontroller",
                "-port", str(self.scep_port)
            ], cwd=self.scep_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"  ✅ SCEP server started on port {self.scep_port}")
            print(f"  🔑 Challenge password: focuscontroller")
            
            return process
            
        except Exception as e:
            print(f"  ❌ Failed to start SCEP server: {e}")
            return None
            
    def get_ca_certificate(self):
        """Download CA certificate from SCEP server"""
        print("📜 Getting CA certificate...")
        
        ca_path = f"{self.certs_dir}/ca.pem"
        
        try:
            # Get CA cert from SCEP server
            url = f"{self.scep_url}/scep?operation=GetCACert"
            
            subprocess.run([
                "curl", url, "-o", f"{self.certs_dir}/ca.der"
            ], check=True)
            
            # Convert to PEM
            subprocess.run([
                "openssl", "x509", "-inform", "DER", "-in", f"{self.certs_dir}/ca.der",
                "-out", ca_path
            ], check=True)
            
            print(f"  ✅ CA certificate saved to {ca_path}")
            return ca_path
            
        except Exception as e:
            print(f"  ❌ Failed to get CA certificate: {e}")
            return None
            
    def start_nanomdm_server(self, ca_path):
        """Start nanomdm server"""
        print("🚀 Starting nanomdm server...")
        
        try:
            # Start nanomdm
            nanomdm_binary = f"{self.nanomdm_dir}/nanomdm-darwin-arm64"
            
            process = subprocess.Popen([
                nanomdm_binary,
                "-ca", ca_path,
                "-api", self.api_key,
                "-debug",
                "-listen", f":{self.nanomdm_port}"
            ], cwd=self.nanomdm_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"  ✅ nanomdm server started on port {self.nanomdm_port}")
            print(f"  🔑 API key: {self.api_key}")
            
            return process
            
        except Exception as e:
            print(f"  ❌ Failed to start nanomdm: {e}")
            return None
            
    def create_enrollment_profile(self, nanomdm_url, scep_url, push_topic):
        """Create iPhone enrollment profile"""
        print("📱 Creating enrollment profile...")
        
        profile_uuid = str(uuid.uuid4())
        scep_uuid = str(uuid.uuid4())
        mdm_uuid = str(uuid.uuid4())
        
        profile = {
            "PayloadContent": [
                # SCEP payload for device certificate
                {
                    "PayloadDisplayName": "Device Certificate",
                    "PayloadIdentifier": "com.focuscontroller.scep",
                    "PayloadType": "com.apple.security.scep",
                    "PayloadUUID": scep_uuid,
                    "PayloadVersion": 1,
                    
                    "URL": f"{scep_url}/scep",
                    "Challenge": "focuscontroller",
                    "Subject": [
                        [ ["CN", "Focus Controller Device"] ],
                        [ ["O", "Focus Controller"] ]
                    ],
                    "KeyType": "RSA",
                    "KeySize": 2048,
                    "KeyUsage": 5,  # Digital signature + Key encipherment
                    "AllowAllAppsAccess": False
                },
                
                # MDM payload
                {
                    "PayloadDisplayName": "Focus Controller MDM",
                    "PayloadIdentifier": "com.focuscontroller.mdm",
                    "PayloadType": "com.apple.mdm",
                    "PayloadUUID": mdm_uuid,
                    "PayloadVersion": 1,
                    
                    "IdentityCertificateUUID": scep_uuid,
                    "Topic": push_topic,
                    "ServerURL": f"{nanomdm_url}/mdm",
                    "CheckInURL": f"{nanomdm_url}/mdm",
                    "CheckOutWhenRemoved": True,
                    
                    "AccessRights": 8191,  # All access rights
                    "UseDevelopmentAPNS": False
                }
            ],
            
            "PayloadDescription": "Focus Controller - Remote iPhone app blocking",
            "PayloadDisplayName": "Focus Controller",
            "PayloadIdentifier": "com.focuscontroller.enrollment",
            "PayloadOrganization": "Focus Controller",
            "PayloadRemovalDisallowed": False,
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        # Save profile
        profile_path = f"{self.base_dir}/FocusController_Enrollment.mobileconfig"
        with open(profile_path, 'wb') as f:
            plistlib.dump(profile, f)
            
        print(f"  ✅ Enrollment profile created: {profile_path}")
        print(f"  📱 Install this profile on your iPhone to enroll it")
        
        return profile_path
        
    def setup_push_certificate(self):
        """Instructions for push certificate setup"""
        print("\n📋 Push Certificate Setup:")
        print("")
        print("To complete the setup, you need an Apple MDM Push Certificate:")
        print("")
        print("1. Go to https://identity.apple.com/")
        print("2. Sign in with your Apple ID")
        print("3. Create an MDM CSR (Certificate Signing Request)")
        print("4. Upload to Apple's Push Certificates Portal")
        print("5. Download the resulting push certificate")
        print("")
        print("Then upload it to nanomdm with:")
        print(f"  cat push.pem push.key | curl -T - -u nanomdm:{self.api_key} '{self.nanomdm_url}/v1/pushcert'")
        print("")
        print("For now, we'll use a placeholder topic...")
        
        # Return a placeholder topic for testing
        return "com.apple.mgmt.External.placeholder"
        
    def run_full_setup(self):
        """Run the complete iPhone setup process"""
        print("🎯 Focus Controller - iPhone Setup")
        print("=" * 50)
        
        # Check requirements
        if not self.check_requirements():
            return False
            
        print("\n" + "="*50)
        
        # Setup SCEP server
        if not self.setup_scep_server():
            return False
            
        print("\n" + "="*50)
        
        # Start SCEP server
        scep_process = self.start_scep_server()
        if not scep_process:
            return False
            
        # Wait a bit for SCEP to start
        import time
        time.sleep(2)
        
        # Get CA certificate
        ca_path = self.get_ca_certificate()
        if not ca_path:
            scep_process.terminate()
            return False
            
        print("\n" + "="*50)
        
        # Start nanomdm server
        nanomdm_process = self.start_nanomdm_server(ca_path)
        if not nanomdm_process:
            scep_process.terminate()
            return False
            
        # Wait for nanomdm to start
        time.sleep(2)
        
        print("\n" + "="*50)
        
        # Setup push certificate (placeholder)
        push_topic = self.setup_push_certificate()
        
        # Create enrollment profile
        profile_path = self.create_enrollment_profile(
            self.nanomdm_url, self.scep_url, push_topic
        )
        
        print("\n" + "="*50)
        print("🎉 Setup Complete!")
        print("")
        print("Next steps:")
        print(f"  1. Transfer {profile_path} to your iPhone")
        print("  2. Install the profile on your iPhone")
        print("  3. Check nanomdm logs for your device ID")
        print("  4. Use Focus Controller app to block apps!")
        print("")
        print("Servers are running:")
        print(f"  • SCEP Server: {self.scep_url}")
        print(f"  • nanomdm Server: {self.nanomdm_url}")
        print("")
        print("Press Ctrl+C to stop servers")
        
        # Keep servers running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            if scep_process:
                scep_process.terminate()
            if nanomdm_process:
                nanomdm_process.terminate()
            print("✅ Servers stopped")
        
        return True
        
def main():
    setup = iPhoneSetup()
    success = setup.run_full_setup()
    
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        exit(1)
        
if __name__ == "__main__":
    main()
