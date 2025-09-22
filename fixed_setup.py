#!/usr/bin/env python3
"""
Fixed Setup Script - Uses actual Mac IP address for iPhone connectivity

This script detects your Mac's IP address and creates a proper enrollment profile
"""

import os
import subprocess
import time
import uuid
import plistlib
import socket
import re

def get_mac_ip():
    """Get Mac's IP address on local network"""
    try:
        # Method 1: Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        
        # Verify it's a local network IP
        if ip.startswith(('192.168.', '10.', '172.')):
            return ip
            
        # Method 2: Parse ifconfig output
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line:
                match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    ip = match.group(1)
                    if ip.startswith(('192.168.', '10.', '172.')):
                        return ip
        
        print("⚠️  Could not detect Mac IP address, using 172.20.10.4")
        return "172.20.10.4"
        
    except Exception as e:
        print(f"⚠️  Error detecting IP: {e}, using 172.20.10.4")
        return "172.20.10.4"

def start_scep_server(bind_ip="0.0.0.0"):
    """Start SCEP server bound to all interfaces"""
    print("🚀 Starting SCEP server...")
    
    scep_binary = "/Users/paul/Files/vsc_projekte/app_block/scep/scepserver"
    
    if not os.path.exists(scep_binary):
        print("❌ SCEP server not found.")
        return None
        
    try:
        # Start SCEP server bound to all interfaces
        process = subprocess.Popen([
            scep_binary,
            "-allowrenew", "0",
            "-challenge", "focuscontroller",
            "-port", "8080",
            "-listen", f"{bind_ip}:8080"
        ], cwd="/Users/paul/Files/vsc_projekte/app_block/scep")
        
        print("✅ SCEP server started on port 8080 (all interfaces)")
        print("🔑 Challenge password: focuscontroller")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start SCEP server: {e}")
        return None

def get_ca_certificate(mac_ip):
    """Get CA certificate from SCEP server"""
    print("📜 Getting CA certificate...")
    
    ca_dir = "/Users/paul/Files/vsc_projekte/app_block/certs"
    os.makedirs(ca_dir, exist_ok=True)
    
    try:
        time.sleep(3)  # Wait for SCEP to start
        
        # Get CA cert from SCEP server using Mac's IP
        ca_url = f"http://{mac_ip}:8080/scep?operation=GetCACert"
        print(f"  Requesting CA cert from: {ca_url}")
        
        subprocess.run([
            "curl", ca_url, "-o", f"{ca_dir}/ca.der"
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
        print("  Make sure SCEP server is running and accessible")
        return None

def start_nanomdm_server(ca_path, bind_ip="0.0.0.0"):
    """Start nanomdm server bound to all interfaces"""
    print("🚀 Starting nanomdm server...")
    
    nanomdm_binary = "/Users/paul/Files/vsc_projekte/app_block/nanomdm/nanomdm-darwin-arm64"
    
    if not os.path.exists(nanomdm_binary):
        print("❌ nanomdm binary not found. Please build it first:")
        print("  cd /Users/paul/Files/vsc_projekte/app_block/nanomdm")
        print("  make my")
        return None
    
    try:
        # Start nanomdm bound to all interfaces
        process = subprocess.Popen([
            nanomdm_binary,
            "-ca", ca_path,
            "-api", "nanomdm",
            "-debug",
            "-listen", f"{bind_ip}:9000"
        ], cwd="/Users/paul/Files/vsc_projekte/app_block/nanomdm")
        
        print("✅ nanomdm server started on port 9000 (all interfaces)")
        print("🔑 API key: nanomdm")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start nanomdm: {e}")
        return None

def create_enrollment_profile(mac_ip):
    """Create enrollment profile for iPhone using Mac's IP"""
    print(f"📱 Creating enrollment profile for Mac IP: {mac_ip}")
    
    profile_uuid = str(uuid.uuid4())
    scep_uuid = str(uuid.uuid4())
    mdm_uuid = str(uuid.uuid4())
    
    # URLs that iPhone can access
    scep_url = f"http://{mac_ip}:8080/scep"
    mdm_url = f"http://{mac_ip}:9000/mdm"
    
    profile = {
        "PayloadContent": [
            # SCEP payload for device certificate
            {
                "PayloadDisplayName": "Device Certificate",
                "PayloadIdentifier": "com.focuscontroller.scep",
                "PayloadType": "com.apple.security.scep",
                "PayloadUUID": scep_uuid,
                "PayloadVersion": 1,
                
                "URL": scep_url,
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
                "ServerURL": mdm_url,
                "CheckInURL": mdm_url,
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
    profile_path = "/Users/paul/Files/vsc_projekte/app_block/FocusController_Fixed.mobileconfig"
    with open(profile_path, 'wb') as f:
        plistlib.dump(profile, f)
        
    print(f"✅ Fixed enrollment profile created: {profile_path}")
    print(f"📱 SCEP URL: {scep_url}")
    print(f"📱 MDM URL: {mdm_url}")
    
    return profile_path

def check_network_connectivity(mac_ip):
    """Check if iPhone can reach the Mac"""
    print(f"🌐 Network connectivity check...")
    print(f"  Mac IP: {mac_ip}")
    print(f"  SCEP will be available at: http://{mac_ip}:8080")
    print(f"  nanomdm will be available at: http://{mac_ip}:9000")
    print("")
    print("⚠️  IMPORTANT: Make sure your iPhone is on the same WiFi network!")
    print("   You can test connectivity by browsing to one of these URLs from your iPhone")

def main():
    print("🎯 Focus Controller - Fixed Setup")
    print("=" * 50)
    
    # Detect Mac's IP address
    mac_ip = get_mac_ip()
    print(f"🖥️  Detected Mac IP: {mac_ip}")
    
    # Check network setup
    check_network_connectivity(mac_ip)
    
    input("\nPress Enter when iPhone and Mac are on same WiFi network...")
    
    print("\n" + "=" * 50)
    
    # Start SCEP server
    scep_process = start_scep_server("0.0.0.0")
    if not scep_process:
        return False
    
    # Get CA certificate
    ca_path = get_ca_certificate(mac_ip)
    if not ca_path:
        scep_process.terminate()
        return False
    
    # Start nanomdm server
    nanomdm_process = start_nanomdm_server(ca_path, "0.0.0.0")
    if not nanomdm_process:
        scep_process.terminate()
        return False
    
    # Wait for servers to start
    time.sleep(3)
    
    # Create enrollment profile with correct IP
    profile_path = create_enrollment_profile(mac_ip)
    
    print("\n" + "=" * 50)
    print("🎉 Fixed Setup Complete!")
    print("")
    print("📱 iPhone Setup Steps:")
    print(f"1. Transfer {profile_path} to your iPhone")
    print("   (AirDrop, email, or any file sharing method)")
    print("2. Open the .mobileconfig file on your iPhone")
    print("3. Follow the installation prompts")
    print("4. The profile should install without errors")
    print("")
    print("🎛️  Next: Launch Focus Controller")
    print("   python3 focus_controller.py")
    print("")
    print("🌐 Servers running:")
    print(f"  • SCEP Server: http://{mac_ip}:8080")
    print(f"  • nanomdm Server: http://{mac_ip}:9000")
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