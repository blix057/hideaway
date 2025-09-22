#!/usr/bin/env python3
"""
Supervised Profile Generator - Creates proper MDM profiles for supervised iOS devices

This creates profiles that can actually block third-party apps like Instagram and YouTube,
but requires the device to be MDM supervised (enrolled through nanomdm).
"""

import uuid
import plistlib
from datetime import datetime
import os

class SupervisedProfileGenerator:
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
        """
        Create a configuration profile that blocks specific apps on supervised devices
        
        Args:
            blocked_apps: List of app bundle IDs to block
            profile_name: Name of the profile
        """
        
        profile_uuid = str(uuid.uuid4())
        restrictions_uuid = str(uuid.uuid4())
        
        # Main profile structure
        profile = {
            "PayloadContent": [],
            "PayloadDescription": f"Blocks selected apps to improve focus and productivity",
            "PayloadDisplayName": profile_name,
            "PayloadIdentifier": f"com.focuscontroller.{profile_name.lower().replace(' ', '')}",
            "PayloadOrganization": "Focus Controller",
            "PayloadRemovalDisallowed": True,  # Make it harder to remove
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1,
            "PayloadScope": "System"  # System-wide restrictions
        }
        
        # App restrictions payload (works on supervised devices)
        restrictions_payload = {
            "PayloadDisplayName": "App Restrictions",
            "PayloadDescription": "Prevents access to specified applications",
            "PayloadIdentifier": "com.focuscontroller.apprestrictions",
            "PayloadType": "com.apple.applicationaccess",
            "PayloadUUID": restrictions_uuid,
            "PayloadVersion": 1,
            
            # Core restriction settings
            "allowAppInstallation": False,  # Prevent new app installs
            "allowAppRemoval": False,      # Prevent app removal
            "allowUIAppInstallation": False,
            
            # App whitelist approach (more reliable on supervised devices)
            # This creates an allowlist - only these apps can run
            # Comment out blacklistedAppBundleIDs and uncomment this for whitelist approach
            # "whitelistedAppBundleIDs": self._get_essential_apps(),
            
            # Blacklist approach - block specific apps
            "blacklistedAppBundleIDs": blocked_apps,
            
            # Additional restrictions
            "allowMultiplayer": False,
            "allowAddingGameCenterFriends": False,
        }
        
        profile["PayloadContent"].append(restrictions_payload)
        
        # Add parental controls payload for extra blocking
        parental_uuid = str(uuid.uuid4())
        parental_payload = {
            "PayloadDisplayName": "Parental Controls",
            "PayloadIdentifier": "com.focuscontroller.parental",
            "PayloadType": "com.apple.familycontrols.contentfilter",
            "PayloadUUID": parental_uuid,
            "PayloadVersion": 1,
            
            # Block by app category
            "restrictedApps": {
                "bundleIdentifiers": blocked_apps
            },
            
            # Time-based restrictions
            "timeRestrictions": {
                "allowedHours": {
                    "start": "06:00",
                    "end": "22:00"
                }
            }
        }
        
        profile["PayloadContent"].append(parental_payload)
        
        # Add web content filtering to block web versions
        web_filter_uuid = str(uuid.uuid4())
        web_filter_payload = {
            "PayloadDisplayName": "Web Content Filter",
            "PayloadIdentifier": "com.focuscontroller.webfilter",
            "PayloadType": "com.apple.webcontent-filter",
            "PayloadUUID": web_filter_uuid,
            "PayloadVersion": 1,
            
            "FilterType": "BuiltIn",
            "AutoFilterEnabled": True,
            "FilterBrowsers": True,
            "FilterSockets": True,
            
            # Block websites related to blocked apps
            "DenyListURLs": self._get_related_websites(blocked_apps)
        }
        
        profile["PayloadContent"].append(web_filter_payload)
        
        return profile
    
    def _get_essential_apps(self):
        """Get list of essential apps to allow (for whitelist approach)"""
        essential_apps = [
            "com.apple.mobilephone",      # Phone
            "com.apple.MobileSMS",        # Messages
            "com.apple.mobilesafari",     # Safari
            "com.apple.mobilemail",       # Mail
            "com.apple.calculator",       # Calculator
            "com.apple.mobilecal",        # Calendar
            "com.apple.reminders",        # Reminders
            "com.apple.mobileaddressbook", # Contacts
            "com.apple.weather",          # Weather
            "com.apple.stocks",           # Stocks
            "com.apple.compass",          # Compass
            "com.apple.VoiceMemos",       # Voice Memos
            "com.apple.MobileStore",      # App Store (if needed)
            "com.apple.Preferences",      # Settings
        ]
        return essential_apps
    
    def _get_related_websites(self, blocked_apps):
        """Get websites to block based on blocked apps"""
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
                "reddit.com", "www.reddit.com", "m.reddit.com",
                "old.reddit.com"
            ],
            "com.netflix.Netflix": [
                "netflix.com", "www.netflix.com"
            ]
        }
        
        websites = []
        for app in blocked_apps:
            if app in website_mapping:
                websites.extend(website_mapping[app])
        
        return websites
    
    def create_unblock_profile(self):
        """Create a profile that removes all restrictions"""
        profile_uuid = str(uuid.uuid4())
        
        profile = {
            "PayloadContent": [],
            "PayloadDescription": "Removes app blocking restrictions",
            "PayloadDisplayName": "Normal Mode - Unblock Apps",
            "PayloadIdentifier": "com.focuscontroller.unblock",
            "PayloadOrganization": "Focus Controller", 
            "PayloadRemovalDisallowed": False,
            "PayloadType": "Configuration",
            "PayloadUUID": profile_uuid,
            "PayloadVersion": 1
        }
        
        # Empty payload to remove restrictions
        return profile
    
    def save_profile(self, profile, filename):
        """Save profile to .mobileconfig file"""
        if not filename.endswith('.mobileconfig'):
            filename += '.mobileconfig'
            
        with open(filename, 'wb') as f:
            plistlib.dump(profile, f)
            
        return filename
    
    def create_focus_profiles_set(self, app_selections):
        """
        Create a set of profiles for different focus modes
        
        Args:
            app_selections: Dict with focus mode names as keys and app lists as values
        """
        profiles = {}
        
        for mode_name, apps in app_selections.items():
            bundle_ids = []
            for app in apps:
                if app in self.app_bundles:
                    bundle_ids.append(self.app_bundles[app])
                else:
                    bundle_ids.append(app)  # Assume it's already a bundle ID
                    
            profiles[mode_name] = self.create_app_blocking_profile(bundle_ids, mode_name)
            
        # Always include an unblock profile
        profiles["Normal Mode"] = self.create_unblock_profile()
        
        return profiles

def main():
    """Example usage"""
    generator = SupervisedProfileGenerator()
    
    # Example: Create different focus modes
    focus_modes = {
        "Deep Work Mode": [
            "Instagram", "YouTube", "TikTok", "Facebook", "Twitter/X", 
            "Snapchat", "Reddit", "Netflix", "Spotify"
        ],
        "Study Mode": [
            "Instagram", "YouTube", "TikTok", "Facebook", "Twitter/X",
            "Snapchat", "Netflix", "Discord", "Twitch"
        ],
        "Social Media Detox": [
            "Instagram", "Facebook", "Twitter/X", "Snapchat", "TikTok", "Reddit"
        ],
        "Entertainment Block": [
            "Netflix", "YouTube", "Spotify", "Disney+", "Twitch"
        ]
    }
    
    # Generate all profiles
    profiles = generator.create_focus_profiles_set(focus_modes)
    
    # Save profiles
    for mode_name, profile in profiles.items():
        filename = f"focus_mode_{mode_name.lower().replace(' ', '_')}.mobileconfig"
        generator.save_profile(profile, filename)
        print(f"Created profile: {filename}")
    
    print(f"\nGenerated {len(profiles)} focus mode profiles:")
    for mode in profiles.keys():
        print(f"  - {mode}")

if __name__ == "__main__":
    main()