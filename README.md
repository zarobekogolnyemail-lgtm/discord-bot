# Protection Bot – Remote Windows PC Control via Discord

A private Discord bot that lets you **remotely monitor and control your own Windows PC** when you are away from home (work, vacation, etc.).

The bot runs on your computer and connects to Discord. You type commands from your phone or another device, and the bot executes them on your PC.

### What you can do
- View a **screenshot** or a **webcam** photo
- **Download a file** from your PC to your phone
- Check **processes**, open windows, CPU/RAM usage
- **Lock**, shut down, or restart the computer
- Record short audio from the microphone or video from the camera
- Enable **automatic startup** with Windows

> ⚠️ **For your own computer only.**  
> This bot has significant system control. Never share the bot token or server access with others.  
> Using such tools on someone else’s device without permission is illegal.

---

## Table of contents

1. [Command list – what each one does](#1-command-list--what-each-one-does)
2. [What you need](#2-what-you-need)
3. [Step-by-step installation](#3-step-by-step-installation)
4. [Running the bot](#4-running-the-bot)
5. [Building an .exe file](#5-building-an-exe-file)
6. [Windows autostart](#6-windows-autostart)
7. [Security](#7-security)
8. [Troubleshooting](#8-troubleshooting)
9. [Usage examples](#9-usage-examples)

---

## 1. Command list – what each one does

All commands start with a dot: **`.`**  
They work **only for you** (your Discord user ID is checked).

### Basic

| Command | What it does |
|---------|----------------|
| `.help` | Shows a short command list on Discord |
| `.status` | CPU, RAM, C: drive, PC name, uptime |
| `.switch` | Lists connected monitors |
| `.switch 0` | Selects monitor 0 (usually primary) for screenshots |
| `.switch 1` | Selects monitor 1 (second screen) for screenshots |

### System and files

| Command | What it does |
|---------|----------------|
| `.cmd <command>` | Runs a Windows system command (e.g. `.cmd ipconfig`) |
| `.ls [path]` | Lists files and folders (works with spaces in names) |
| `.download <path>` | Downloads a file from the PC to Discord (limit ~24 MB) |
| `.upload` | Attach a file on Discord → bot saves it to disk |
| `.procs` | Top processes by RAM usage |
| `.windows` | List of open window titles |
| `.kill <name>` | Closes a process (e.g. `.kill chrome`) |
| `.clipboard` | Shows current clipboard text (Ctrl+C content) |

### Screen / camera / microphone

| Command | What it does |
|---------|----------------|
| `.ss` | Single screenshot (selected monitor) |
| `.sslive on` | Sends a new screenshot every 3 seconds |
| `.sslive off` | Stops continuous screenshots |
| `.webcam` | Single photo from the webcam |
| `.camrec 5` | Records camera video (default 5 s, max 12 s) |
| `.mic 5` | Records microphone audio (default 5 s, max 15 s) |
| `.choosemic` | Lists available microphones |
| `.choosemic 2` | Selects microphone number 2 for recording |

### Audio

| Command | What it does |
|---------|----------------|
| `.soundplay` | Plays an attached MP3/WAV/OGG file on the PC speakers |
| `.soundstop` | Stops playback |
| `.volume 50` | Sets system volume (0–100, approximate) |
| `.volup` | Increases volume |
| `.voldown` | Decreases volume |
| `.mute` | Toggles system mute |

### Power

| Command | What it does |
|---------|----------------|
| `.lock` | Locks the computer (Windows lock screen) |
| `.shutdown` | Shuts down the PC in 10 seconds |
| `.restart` | Restarts the PC in 10 seconds |
| `.battery` | Shows battery level (laptops) |

### Other

| Command | What it does |
|---------|----------------|
| `.open google.com` | Opens a website in the default browser |
| `.notify text` | Shows a Windows notification |
| `.join` | Lists voice channels on the server |
| `.join general` | Bot joins the voice channel with that name |
| `.leave` | Bot leaves the voice channel |
| `.autoon` | Enables bot startup with Windows |
| `.autooff` | Disables autostart |
| `.autostatus` | Checks whether autostart is enabled |
| `.destroy` | Immediately stops the bot process |

---

## 2. What you need

| Item | Why |
|------|-----|
| **Windows 10 or 11** | The bot is built for Windows |
| **Discord account** | To create the bot and send commands |
| **Python 3.10+** | Language the script runs on |
| **Visual Studio Code** (or another editor) | To paste and edit the code |
| **`ochrona.py` file** | The bot source code |
| **Your own Discord server** (preferably private) | Where the bot will run |

---

## 3. Step-by-step installation

### Step A – Install Python

1. Go to: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Click the big yellow **Download Python 3.x.x** button
3. Run the installer
4. **On the first screen, check at the bottom:**
   - ✅ **Add python.exe to PATH**
5. Click **Install Now** and wait until it finishes
6. Close the installer
7. Open **PowerShell**:
   - Press the Windows key → type `powershell` → Enter
8. Run:

```powershell
python --version
