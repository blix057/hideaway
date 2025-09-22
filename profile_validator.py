#!/usr/bin/env python3
"""
Profile Validator - Tool to validate mobileconfig files for common issues

This tool checks iOS configuration profiles for structural issues that might
cause "PayloadContent missing" or other installation errors.
"""

import sys
import plistlib
import os
from pathlib import Path

def validate_profile(profile_path):
    """Validate a mobileconfig profile file"""
    print(f"🔍 Validating profile: {profile_path}")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(profile_path):
        print("❌ File does not exist")
        return False
        
    try:
        # Load and parse the profile
        with open(profile_path, 'rb') as f:
            profile = plistlib.load(f)
    except Exception as e:
        print(f"❌ Failed to parse plist: {e}")
        return False
        
    issues_found = 0
    
    # Check required root level fields
    required_fields = [
        'PayloadContent',
        'PayloadDescription', 
        'PayloadDisplayName',
        'PayloadIdentifier',
        'PayloadType',
        'PayloadUUID',
        'PayloadVersion'
    ]
    
    print("📋 Root Level Validation:")
    for field in required_fields:
        if field in profile:
            print(f"  ✅ {field}: Present")
        else:
            print(f"  ❌ {field}: MISSING")
            issues_found += 1
            
    # Validate PayloadType
    if profile.get('PayloadType') != 'Configuration':
        print(f"  ❌ PayloadType should be 'Configuration', got: {profile.get('PayloadType')}")
        issues_found += 1
    else:
        print(f"  ✅ PayloadType: Correct")
        
    # Validate PayloadVersion
    if profile.get('PayloadVersion') != 1:
        print(f"  ❌ PayloadVersion should be 1, got: {profile.get('PayloadVersion')}")
        issues_found += 1
    else:
        print(f"  ✅ PayloadVersion: Correct")
        
    # Check PayloadContent
    payload_content = profile.get('PayloadContent', [])
    print(f"\n📦 PayloadContent Validation:")
    print(f"  Number of payloads: {len(payload_content)}")
    
    if not isinstance(payload_content, list):
        print(f"  ❌ PayloadContent must be an array, got: {type(payload_content)}")
        issues_found += 1
        return issues_found == 0
        
    if len(payload_content) == 0:
        print(f"  ⚠️  PayloadContent is empty (this might be intentional for removal profiles)")
    
    # Validate each payload
    for i, payload in enumerate(payload_content):
        print(f"\n  📄 Payload {i+1}:")
        
        if not isinstance(payload, dict):
            print(f"    ❌ Payload must be a dictionary, got: {type(payload)}")
            issues_found += 1
            continue
            
        # Required payload fields
        payload_required = [
            'PayloadDisplayName',
            'PayloadIdentifier', 
            'PayloadType',
            'PayloadUUID',
            'PayloadVersion'
        ]
        
        for field in payload_required:
            if field in payload:
                print(f"    ✅ {field}: {payload[field]}")
            else:
                print(f"    ❌ {field}: MISSING")
                issues_found += 1
                
        # Validate payload types
        payload_type = payload.get('PayloadType', '')
        if payload_type:
            if payload_type.startswith('com.apple.'):
                print(f"    ✅ PayloadType looks valid: {payload_type}")
            else:
                print(f"    ⚠️  PayloadType doesn't start with com.apple.: {payload_type}")
                
        # Check for common app blocking payload types
        if payload_type == 'com.apple.applicationaccess':
            print(f"    ℹ️  App restriction payload detected")
            if 'blacklistedAppBundleIDs' in payload:
                bundle_ids = payload['blacklistedAppBundleIDs']
                print(f"    📱 Blocking {len(bundle_ids)} apps")
                for bundle_id in bundle_ids[:3]:  # Show first 3
                    print(f"      - {bundle_id}")
                if len(bundle_ids) > 3:
                    print(f"      ... and {len(bundle_ids) - 3} more")
                    
    # Summary
    print(f"\n📊 Validation Summary:")
    if issues_found == 0:
        print(f"  ✅ Profile appears valid! No issues found.")
        return True
    else:
        print(f"  ❌ Found {issues_found} issue(s) that need to be fixed.")
        return False

def validate_all_profiles(directory="."):
    """Validate all .mobileconfig files in a directory"""
    profile_files = list(Path(directory).glob("*.mobileconfig"))
    
    if not profile_files:
        print("No .mobileconfig files found in the current directory")
        return
        
    print(f"Found {len(profile_files)} profile(s) to validate:\n")
    
    results = {}
    for profile_file in profile_files:
        results[profile_file.name] = validate_profile(str(profile_file))
        print("\n" + "="*80 + "\n")
        
    # Summary
    print("🎯 FINAL SUMMARY:")
    valid_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for filename, is_valid in results.items():
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"  {filename}: {status}")
        
    print(f"\nValidated: {valid_count}/{total_count} profiles are valid")

def create_minimal_test_profile():
    """Create a minimal test profile for testing"""
    import uuid
    
    profile = {
        'PayloadContent': [
            {
                'PayloadDisplayName': 'Test Restriction',
                'PayloadIdentifier': 'com.test.restriction',
                'PayloadType': 'com.apple.applicationaccess', 
                'PayloadUUID': str(uuid.uuid4()),
                'PayloadVersion': 1,
                'blacklistedAppBundleIDs': ['com.burbn.instagram']
            }
        ],
        'PayloadDescription': 'Test profile for validation',
        'PayloadDisplayName': 'Test Profile', 
        'PayloadIdentifier': 'com.test.profile',
        'PayloadOrganization': 'Test',
        'PayloadRemovalDisallowed': False,
        'PayloadType': 'Configuration',
        'PayloadUUID': str(uuid.uuid4()),
        'PayloadVersion': 1
    }
    
    filename = 'test_profile.mobileconfig'
    with open(filename, 'wb') as f:
        plistlib.dump(profile, f)
        
    print(f"✅ Created minimal test profile: {filename}")
    return filename

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate iOS configuration profiles")
    parser.add_argument('files', nargs='*', help='Profile files to validate')
    parser.add_argument('--all', action='store_true', help='Validate all .mobileconfig files in current directory')
    parser.add_argument('--create-test', action='store_true', help='Create a minimal test profile')
    
    args = parser.parse_args()
    
    if args.create_test:
        filename = create_minimal_test_profile()
        validate_profile(filename)
    elif args.all:
        validate_all_profiles()
    elif args.files:
        for file in args.files:
            validate_profile(file)
            print("\n" + "="*80 + "\n")
    else:
        validate_all_profiles()

if __name__ == "__main__":
    main()