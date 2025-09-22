# 🎯 Hideaway - Bundled Version

This is the **single-file bundled version** of Hideaway - a macOS app for remotely blocking iPhone apps via MDM.

## 📦 What's Different in the Bundled Version?

- **Single File**: All functionality is bundled into `hideaway_bundled.py` - no dependencies on other files
- **Desktop Profiles**: All enrollment and blocking profiles are saved to your **Desktop** for easy access
- **Simplified Setup**: Everything works from one file, making distribution easier

## 🚀 Quick Start

1. **Run the app**:
   ```bash
   python3 hideaway_bundled.py
   ```

2. **Setup iPhone**:
   - Click "📱 Setup iPhone" 
   - An enrollment profile will be saved to your Desktop
   - Transfer it to your iPhone and install

3. **Block Apps**:
   - Click "🎛️ Launch Hideaway"
   - Select apps to block
   - Profiles will be saved to your Desktop for transfer to iPhone

## 📁 File Locations

All profiles are saved to your **Desktop**:
- `Hideaway_Enrollment.mobileconfig` - For iPhone enrollment
- `hideaway_profile_YYYYMMDD_HHMMSS.mobileconfig` - Blocking profiles
- `hideaway_focus_*.mobileconfig` - Pre-made focus mode profiles

## 📱 How to Use Profiles

1. **Transfer to iPhone**: Use AirDrop, email, or file sharing
2. **Install Profile**: Open the .mobileconfig file on your iPhone
3. **Trust Certificate**: Go to Settings > General > About > Certificate Trust Settings

## ✨ Features

- Block Instagram, YouTube, TikTok, Facebook, Twitter/X, and more
- Pre-made focus modes (Study, Work, Social Media Detox)
- Web content filtering to block websites too
- Simple one-click blocking/unblocking
- All profiles saved to Desktop for easy access

## 🔧 Requirements

- macOS with Python 3
- iPhone capable of MDM enrollment
- Same WiFi network (for full MDM functionality)

## 💡 Tips

- Keep the bundled Python file in a safe location
- All profiles will appear on your Desktop - organize them as needed  
- For best results, enroll your iPhone in supervised mode
- This version is perfect for sharing with others - just send them the single file!

---

**Hideaway Bundled** - One file, full functionality! 🎯📱