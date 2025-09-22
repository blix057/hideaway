# 🎯 Hideaway - Remote iPhone App Blocker

A macOS application that lets you remotely block distracting apps on your iPhone via WiFi using Apple's MDM (Mobile Device Management) system.

## ✨ Features

- **Remote Control**: Block/unblock iPhone apps from your Mac
- **One-Click Toggle**: Simple button to enable/disable blocking
- **Comprehensive App Database**: Pre-configured with popular apps (Instagram, YouTube, TikTok, etc.)
- **Website Blocking**: Also blocks web versions of apps in Safari
- **Focus Modes**: Pre-built profiles for different scenarios (Study Mode, Deep Work, etc.)
- **Real-time Control**: Changes take effect immediately via push notifications
- **Activity Logging**: See exactly what's happening with detailed logs

## 📱 How It Works

```
Mac App (Controller) ←→ nanomdm Server ←→ iPhone (MDM Enrolled)
     ↓                        ↓                    ↓
 Select Apps             Generate Profile      Apps Blocked
 Hit Switch             Push to Device        Via Restrictions
```

The system uses Apple's official MDM protocols to push configuration profiles that block specified apps at the system level.

## 🚀 Quick Start

1. **Launch the system**:
   ```bash
   cd /Users/paul/Files/vsc_projekte/hideaway
   python3 run_hideaway.py
   ```

2. **Setup your iPhone** (first time only):
   - Click "📱 Setup iPhone" 
   - Follow the enrollment instructions
   - Install the profile on your iPhone

3. **Start blocking apps**:
   - Click "🎛️ Launch Controller"
   - Enter your device ID
   - Select apps to block
   - Hit "🔴 BLOCK APPS"

## 📂 Project Structure

```
hideaway/
├── run_hideaway.py      # 🎯 Main launcher GUI
├── hideaway_controller.py          # 🎛️ Core Mac control app
├── setup_iphone.py             # 📱 iPhone enrollment automation
├── supervised_profile_generator.py # 📋 Profile creation system
├── deploy_hideaway.py          # 🚀 Profile deployment script
└── nanomdm/                     # 🔧 MDM server (cloned repo)
    ├── nanomdm-darwin-arm64     # Built MDM server binary
    └── tools/cmdr.py           # Command generation tool
```

## 🔧 System Components

### 1. Hideaway Controller (`hideaway_controller.py`)
- **GUI application** for selecting apps and controlling blocking
- **Real-time status** and activity logging  
- **Connection testing** to verify iPhone communication
- **Pre-configured app database** with bundle IDs

### 2. iPhone Setup (`setup_iphone.py`)
- **Automated SCEP server** setup for device certificates
- **nanomdm server** startup and configuration
- **Enrollment profile** generation for iPhone
- **Certificate management** for secure MDM communication

### 3. Profile Generator (`supervised_profile_generator.py`)
- **Dynamic profile creation** for app blocking
- **Multiple restriction types** (app blacklist, web filtering)
- **Focus mode profiles** (Study, Work, Social Media Detox)
- **Website blocking** for web versions of apps

### 4. Main Launcher (`run_hideaway.py`)
- **Unified interface** for all system components
- **Setup wizard** for first-time configuration
- **Help system** with troubleshooting guides
- **Profile management** tools

## 📱 Supported Apps

### Social Media
- Instagram, YouTube, TikTok, Facebook, Twitter/X
- Snapchat, Reddit, Discord, LinkedIn, Pinterest

### Entertainment  
- Netflix, Disney+, Spotify, Twitch
- Amazon Prime Video

### Apple Apps
- Safari, Camera, Photos, Music, App Store
- Messages, Mail, FaceTime, Maps, News

### Games & Others
- Popular mobile games, messaging apps
- **Easy to add more** - just add the bundle ID

## ⚙️ Technical Requirements

### Mac Requirements
- **macOS** (tested on macOS with Apple Silicon)
- **Python 3** with tkinter, requests, plistlib
- **Go** (for building nanomdm)
- **OpenSSL** and curl

### iPhone Requirements  
- **iOS device** capable of MDM enrollment
- **Same WiFi network** as Mac
- **MDM supervision** (enrolled via the setup process)

### Network Requirements
- **Local network access** between Mac and iPhone
- **Internet access** for downloading SCEP server and certificates

## 🔐 Security & Privacy

- **Uses Apple's official MDM protocols** - no jailbreaking required
- **Certificates are managed securely** via SCEP
- **All communication is encrypted** using TLS
- **No data collection** - everything runs locally
- **Open source** - you can audit the entire codebase

## ⚠️ Important Limitations

### What Works ✅
- **Third-party app blocking** (Instagram, YouTube, etc.) on supervised devices
- **Apple app restrictions** (Safari, Camera, etc.)
- **Website blocking** via content filtering  
- **Real-time profile deployment** via push notifications

### What Requires MDM Supervision ⚠️
- **Blocking third-party apps** like Instagram requires the device to be MDM supervised
- **Some advanced restrictions** only work in supervised mode
- **Profile removal restrictions** work better on supervised devices

### What Doesn't Work ❌
- **Non-supervised devices** have very limited app blocking capabilities
- **System-level apps** that can't be restricted via MDM
- **Apps installed via enterprise** or development certificates

## 🛠️ Troubleshooting

### Connection Issues
- Verify both devices are on the same WiFi network
- Check that nanomdm server is running (port 9000)  
- Make sure SCEP server is accessible (port 8080)
- Try restarting the servers

### Profile Installation
- Make sure the enrollment profile was installed correctly
- Check that the device shows up in nanomdm logs
- Verify the device ID matches what you entered

### App Blocking Not Working
- Confirm the device is MDM supervised
- Check that the profile was successfully installed
- Some apps may require a device restart to be blocked
- Verify the bundle IDs are correct for your region

### Server Errors
- Check that ports 8080 and 9000 are not in use
- Make sure you have proper certificates set up
- Verify Go and Python dependencies are installed

## 🔮 Future Enhancements

- **Time-based restrictions** (block apps during work hours)
- **Usage limits** (allow 30 minutes of Instagram per day)
- **Multiple device support** (manage multiple iPhones)  
- **Cloud sync** (sync settings across devices)
- **Analytics** (see usage patterns and blocking effectiveness)
- **Shortcuts integration** (Siri commands to enable/disable blocking)

## 📄 License

This project builds on **nanomdm** which is licensed under the MIT License.

The Hideaway components are also released under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Areas where help is needed:

- **Additional app bundle IDs** for more comprehensive blocking
- **UI/UX improvements** for better user experience
- **Testing on different iOS versions** and device types  
- **Documentation** and tutorial improvements
- **Bug reports** and feature requests

## 📧 Support

If you run into issues:

1. Check the **Help & Instructions** in the launcher
2. Look at the **activity logs** in Hideaway Controller
3. Verify your **setup** matches the requirements
4. Check the **troubleshooting** section above

---

**Hideaway** - Take control of your iPhone distractions from your Mac! 🎯📱
