# RFID Kiosk Player

<p align="center">
  <img src="icon_new.png" alt="RFID Kiosk Player" width="128">
</p>

<p align="center">
  <img src="logo_new.png" alt="RFID Kiosk Player Logo" width="500">
</p>

A Windows application that plays videos triggered by RFID card scans. Perfect for interactive kiosk displays, museums, exhibitions, and trade shows.

## ✨ Features

- 🎬 **Default Loop Video** - Plays continuously when no card is scanned
- 💳 **RFID Card Triggers** - Assign different videos to different RFID cards
- 🔄 **Configurable Loops** - Set how many times each trigger video plays
- 🔙 **Return to Default** - Special card to instantly return to default video
- 📺 **Fullscreen Playback** - Immersive kiosk experience
- 📝 **Scan Logging** - Automatic logging of all card scans with timestamps
- ⚙️ **Easy Configuration** - User-friendly settings interface

## 🚀 Quick Start

1. Download the latest release
2. Run `kiosk_player.exe`
3. Configure your default video and RFID card mappings
4. Click "Save and Start Player"

## 📋 Requirements

- Windows 10/11
- USB RFID Card Reader (acts as keyboard input)
- Video files (MP4, AVI, MKV supported)

## ⚙️ Configuration

### Default Loop Video

Select a video that will play continuously in the background.

### RFID Card Triggers

1. Scan an RFID card to see its ID
2. Enter the ID in the settings
3. Assign a video file to that ID
4. Set the number of loops (1-100)

### Return to Default Card

Optionally assign a special card that immediately returns to the default video.

## 🎯 Use Cases

- **Museums** - Trigger informational videos at exhibits
- **Trade Shows** - Interactive product demonstrations
- **Retail** - Customer-triggered promotional content
- **Education** - Interactive learning stations
- **Events** - Personalized welcome messages

## 📁 Files

- `config.json` - Stores your settings (auto-generated)
- `scan_log.txt` - Log of all RFID scans with timestamps

## 🛠️ Building from Source

```bash
# Install dependencies
pip install opencv-python pillow pyinstaller

# Build executable
pyinstaller kiosk_player.spec
```

## ⌨️ Controls

| Key          | Action                 |
| ------------ | ---------------------- |
| `Q` or `ESC` | Exit player            |
| RFID Scan    | Trigger assigned video |

## 📝 License

MIT License - Feel free to use and modify.

## 👤 Author

**Bora İncesu**

---

Made with ❤️ for interactive displays
