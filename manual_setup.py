#!/usr/bin/env python3
"""
Manual Setup Script - Quick setup for Focus Controller when automatic setup fails

This script manually sets up the required servers for Focus Controller
"""

import os
import subprocess
import time
import uuid
import plistlib

def start_scep_server():
    """Start SCEP server manually"""
    print("🚀 Starting SCEP server...")
    
    scep_binary = "/Users/paul/Files/vsc_projekte/app_block/scep/scepserver"
    
    if not os.path.exists(scep_binary):
        print("❌ SCEP server not found. Please run the automatic setup first.")
        return None
        
    try:
        # Start SCEP server
        process = subprocess.Popen([
            scep_binary,
            "-allowrenew", "0",
            "-challenge", "focuscontroller",
            "-port", "8080"
        ], cwd="/Users/paul/Files/vsc_projekte/app_block/scep")
        
        print("✅ SCEP server started on port 8080")
        print("🔑 Challenge password: focuscontroller")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start SCEP server: {e}")
        return None

def get_ca_certificate():
    """Get CA certificate from SCEP server"""
    print("📜 Getting CA certificate...")
    
    ca_dir = "/Users/paul/Files/vsc_projekte/app_block/certs"
    os.makedirs(ca_dir, exist_ok=True)
    
    try:
        time.sleep(2)  # Wait for SCEP to start
        
        # Get CA cert from SCEP server
        subprocess.run([
            "curl", "http://127.0.0.1:8080/scep?operation=GetCACert",
            "-o", f"{ca_dir}/ca.der"
        ], check=True)
        
        # Convert to PEM
        subprocess.run([
            "openssl", "x509", "-inform", "DER", "-in", f"{ca_dir}/ca.der",
            "-out", f"{ca_dir}/ca.pem"
        ], check=True)
        
        print(f"✅ CA certificate saved to {ca_dir}/ca.pem")
        return f"{ca_dir}/ca.pem"
        
    except Exception as e:
        print(f"❌ Failed to get CA certificate: {e}")
        return None

def start_nanomdm_server(ca_path):
    """Start nanomdm server"""
    print("🚀 Starting nanomdm server...")
    
    nanomdm_binary = "/Users/paul/Files/vsc_projekte/app_block/nanomdm/nanomdm-darwin-arm64"
    
    if not os.path.exists(nanomdm_binary):
        print("❌ nanomdm binary not found. Please build it first:")
        print("  cd /Users/paul/Files/vsc_projekte/app_block/nanomdm")
        print("  make my")
        return None
    
    try:
        # Start nanomdm
        process = subprocess.Popen([
            nanomdm_binary,
            "-ca", ca_path,
            "-api", "nanomdm",
            "-debug",
            "-listen", ":9000"
        ], cwd="/Users/paul/Files/vsc_projekte/app_block/nanomdm")
        
        print("✅ nanomdm server started on port 9000")
        print("🔑 API key: nanomdm")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start nanomdm: {e}")
        return None

def create_enrollment_profile():
    """Create enrollment profile for iPhone"""
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
                
                "URL": "http://127.0.0.1:8080/scep",
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
                "Topic": "com.apple.mgmt.External.placeholder",
                "ServerURL": "http://127.0.0.1:9000/mdm",
                "CheckInURL": "http://127.0.0.1:9000/mdm",
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
    profile_path = "/Users/paul/Files/vsc_projekte/app_block/FocusController_Enrollment.mobileconfig"
    with open(profile_path, 'wb') as f:
        plistlib.dump(profile, f)
        
    print(f"✅ Enrollment profile created: {profile_path}")
    return profile_path

def main():
    print("🎯 Focus Controller - Manual Setup")
    print("=" * 50)
    
    # Start SCEP server
    scep_process = start_scep_server()
    if not scep_process:
        return False
    
    # Get CA certificate
    ca_path = get_ca_certificate()
    if not ca_path:
        scep_process.terminate()
        return False
    
    # Start nanomdm server
    nanomdm_process = start_nanomdm_server(ca_path)
    if not nanomdm_process:
        scep_process.terminate()
        return False
    
    # Wait for servers to start
    time.sleep(3)
    
    # Create enrollment profile
    profile_path = create_enrollment_profile()
    
    print("\n" + "=" * 50)
    print("🎉 Manual Setup Complete!")
    print("")
    print("Next steps:")
    print(f"1. Transfer {profile_path} to your iPhone")
    print("2. Install the profile on your iPhone")
    print("3. Note your device ID from nanomdm logs")
    print("4. Launch Focus Controller:")
    print("   python3 focus_controller.py")
    print("")
    print("Servers are running:")
    print("  • SCEP Server: http://127.0.0.1:8080")
    print("  • nanomdm Server: http://127.0.0.1:9000")
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

if __name__ == "__main__":
    main()