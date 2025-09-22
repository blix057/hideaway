#!/usr/bin/env python3
"""
Simple Profile Generator - Creates basic, reliable iOS configuration profiles

This version uses only the most reliable payload types that are well-supported
across iOS versions to avoid "PayloadContent missing" errors.
"""

import uuid
import plistlib
import os

class SimpleProfileGenerator:
    def __init__(self):
        # App bundle database (same as before)
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
            
            # Apple Apps (these work reliably on supervised devices)
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
        
    def create_simple_app_blocking_profile(self, blocked_apps, profile_name="App Block"):
        """
        Create a simple, reliable configuration profile using only basic app restrictions
        
        Args:
            blocked_apps: List of app bundle IDs to block
            profile_name: Name of the profile
        """
        
        profile_uuid = str(uuid.uuid4())
        restrictions_uuid = str(uuid.uuid4())
        
        # Main profile structure - minimal but complete
        profile = {
            "PayloadContent": [],
            "PayloadDescription": f"Blocks specified apps: {', '.join(blocked_apps[:3])}{'...' if len(blocked_apps) > 3 else ''}",
            "PayloadDisplayName": profile_name,
            "PayloadIdentifier": f"com.focuscontroller.{profile_name.lower().replace(' ', '').replace('-', '')}",
            "PayloadOrganization": "Focus Controller",
            "PayloadRemovalDisallowed": False,  # Allow removal for testing
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        # Only use the basic app restrictions payload (most reliable)
        if blocked_apps:
            restrictions_payload = {
                "PayloadDisplayName": "App Access Restrictions",
                "PayloadDescription": "Restricts access to specified applications",
                "PayloadIdentifier": "com.focuscontroller.apprestrictions",
                "PayloadType": "com.apple.applicationaccess",
                "PayloadUUID": restrictions_uuid,
                "PayloadVersion": 1,
                
                # Use blacklist approach - this is well supported
                "blacklistedAppBundleIDs": blocked_apps
            }
            
            profile["PayloadContent"].append(restrictions_payload)
        
        return profile
    
    def create_web_blocking_profile(self, blocked_websites, profile_name="Web Block"):
        """
        Create a profile that blocks specific websites using web content filter
        """
        
        profile_uuid = str(uuid.uuid4())
        filter_uuid = str(uuid.uuid4())
        
        profile = {
            "PayloadContent": [
                {
                    "PayloadDisplayName": "Web Content Filter",
                    "PayloadDescription": "Blocks specified websites",
                    "PayloadIdentifier": "com.focuscontroller.webfilter",
                    "PayloadType": "com.apple.webcontent-filter",
                    "PayloadUUID": filter_uuid,
                    "PayloadVersion": 1,
                    
                    "FilterType": "BuiltIn",
                    "AutoFilterEnabled": True,
                    "FilterBrowsers": True,
                    "FilterSockets": True,
                    "DenyListURLs": blocked_websites
                }
            ],
            "PayloadDescription": f"Blocks websites: {', '.join(blocked_websites[:3])}{'...' if len(blocked_websites) > 3 else ''}",
            "PayloadDisplayName": profile_name,
            "PayloadIdentifier": f"com.focuscontroller.{profile_name.lower().replace(' ', '').replace('-', '')}",
            "PayloadOrganization": "Focus Controller",
            "PayloadRemovalDisallowed": False,
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        return profile
    
    def create_removal_profile(self):
        """Create a profile that removes restrictions (empty PayloadContent)"""
        
        profile_uuid = str(uuid.uuid4())
        
        profile = {
            "PayloadContent": [],  # Empty content removes restrictions
            "PayloadDescription": "Removes app blocking restrictions",
            "PayloadDisplayName": "Remove Restrictions",
            "PayloadIdentifier": "com.focuscontroller.remove",
            "PayloadOrganization": "Focus Controller",
            "PayloadRemovalDisallowed": False,
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        return profile
    
    def get_website_list_for_apps(self, app_bundle_ids):
        """Get corresponding websites for blocked apps"""
        
        website_mapping = {
            "com.burbn.instagram": [
                "instagram.com", "www.instagram.com", "m.instagram.com"
            ],
            "com.google.ios.youtube": [
                "youtube.com", "www.youtube.com", "m.youtube.com", 
                "youtu.be", "music.youtube.com"
            ],
            "com.zhiliaoapp.musically": [
                "tiktok.com", "www.tiktok.com", "m.tiktok.com"
            ],
            "com.facebook.Facebook": [
                "facebook.com", "www.facebook.com", "m.facebook.com"
            ],
            "com.twitter.twitter": [
                "twitter.com", "www.twitter.com", "m.twitter.com",
                "x.com", "www.x.com"
            ],
            "com.reddit.Reddit": [
                "reddit.com", "www.reddit.com", "m.reddit.com", "old.reddit.com"
            ],
            "com.netflix.Netflix": [
                "netflix.com", "www.netflix.com"
            ]
        }
        
        websites = []
        for app_id in app_bundle_ids:
            if app_id in website_mapping:
                websites.extend(website_mapping[app_id])
        
        return websites
    
    def create_combo_profile(self, blocked_apps, profile_name="Focus Mode"):
        """
        Create a profile that blocks both apps and their corresponding websites
        """
        
        websites = self.get_website_list_for_apps(blocked_apps)
        
        profile_uuid = str(uuid.uuid4())
        app_restrictions_uuid = str(uuid.uuid4())
        web_filter_uuid = str(uuid.uuid4())
        
        profile = {
            "PayloadContent": [],
            "PayloadDescription": f"Blocks {len(blocked_apps)} apps and {len(websites)} websites",
            "PayloadDisplayName": profile_name,
            "PayloadIdentifier": f"com.focuscontroller.{profile_name.lower().replace(' ', '').replace('-', '')}",
            "PayloadOrganization": "Focus Controller",
            "PayloadRemovalDisallowed": False,
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        # Add app restrictions
        if blocked_apps:
            app_payload = {
                "PayloadDisplayName": "App Restrictions",
                "PayloadDescription": "Blocks specified applications",
                "PayloadIdentifier": "com.focuscontroller.apprestrictions",
                "PayloadType": "com.apple.applicationaccess",
                "PayloadUUID": app_restrictions_uuid,
                "PayloadVersion": 1,
                "blacklistedAppBundleIDs": blocked_apps
            }
            profile["PayloadContent"].append(app_payload)
        
        # Add web filtering
        if websites:
            web_payload = {
                "PayloadDisplayName": "Website Restrictions",
                "PayloadDescription": "Blocks specified websites",
                "PayloadIdentifier": "com.focuscontroller.webfilter",
                "PayloadType": "com.apple.webcontent-filter",
                "PayloadUUID": web_filter_uuid,
                "PayloadVersion": 1,
                "FilterType": "BuiltIn",
                "AutoFilterEnabled": True,
                "FilterBrowsers": True,
                "FilterSockets": True,
                "DenyListURLs": websites
            }
            profile["PayloadContent"].append(web_payload)
            
        return profile
    
    def save_profile(self, profile, filename):
        """Save profile to .mobileconfig file"""
        if not filename.endswith('.mobileconfig'):
            filename += '.mobileconfig'
            
        with open(filename, 'wb') as f:
            plistlib.dump(profile, f)
            
        print(f"✅ Saved profile: {filename}")
        return filename
    
    def create_focus_modes(self):
        """Create simple, reliable focus mode profiles"""
        
        focus_modes = {
            "Social Media Block": ["Instagram", "Facebook", "Twitter/X", "Snapchat", "TikTok", "Reddit"],
            "Study Mode": ["Instagram", "YouTube", "TikTok", "Netflix", "Discord"],
            "Work Focus": ["Instagram", "YouTube", "TikTok", "Facebook", "Twitter/X", "Reddit"],
        }
        
        profiles_created = []
        
        for mode_name, app_names in focus_modes.items():
            # Convert app names to bundle IDs
            bundle_ids = []
            for app_name in app_names:
                if app_name in self.app_bundles:
                    bundle_ids.append(self.app_bundles[app_name])
            
            if bundle_ids:
                # Create combo profile (apps + websites)
                profile = self.create_combo_profile(bundle_ids, mode_name)
                filename = f"simple_{mode_name.lower().replace(' ', '_')}.mobileconfig"
                self.save_profile(profile, filename)
                profiles_created.append(filename)
        
        # Create removal profile
        removal_profile = self.create_removal_profile()
        removal_filename = "simple_remove_restrictions.mobileconfig"
        self.save_profile(removal_profile, removal_filename)
        profiles_created.append(removal_filename)
        
        return profiles_created

def main():
    """Create simple test profiles"""
    print("🎯 Simple Profile Generator - Creating reliable profiles...")
    print("=" * 60)
    
    generator = SimpleProfileGenerator()
    
    # Create focus mode profiles
    profiles = generator.create_focus_modes()
    
    print(f"\n✅ Created {len(profiles)} profiles:")
    for profile in profiles:
        print(f"  - {profile}")
        
    print("\nThese profiles use only basic, well-supported payload types.")
    print("Try installing one of these on your iPhone to test.")

if __name__ == "__main__":
    main()