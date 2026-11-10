# Ochrona Bot – zdalne zarządzanie komputerem Windows przez Discord

Prywatny bot Discord, który pozwala **zdalnie pilnować i obsługiwać własny komputer Windows**, gdy jesteś poza domem.

Możesz m.in.:
- zobaczyć zrzut ekranu albo obraz z kamerki
- pobrać plik z komputera na telefon
- sprawdzić, co jest uruchomione
- zablokować / wyłączyć / zrestartować PC
- włączyć automatyczny start bota razem z Windows

> ⚠️ **Tylko do własnego komputera.**  
> Bot ma dużą kontrolę nad systemem. Nie dawaj tokena ani dostępu innym osobom.

---

## Spis treści

1. [Co robi bot – lista komend](#1-co-robi-bot--lista-komend)
2. [Czego potrzebujesz](#2-czego-potrzebujesz)
3. [Krok po kroku – instalacja](#3-krok-po-kroku--instalacja)
4. [Uruchomienie bota](#4-uruchomienie-bota)
5. [Opcjonalnie: plik .exe](#5-opcjonalnie-plik-exe)
6. [Auto-start z Windows](#6-auto-start-z-windows)
7. [Bezpieczeństwo](#7-bezpieczeństwo)
8. [Problemy i rozwiązania](#8-problemy-i-rozwiązania)

---

## 1. Co robi bot – lista komend

Prefix komend: **`.`** (kropka)

### Podstawowe
| Komenda | Do czego służy |
|---------|----------------|
| `.help` | Pokazuje listę komend |
| `.status` | Pokazuje obciążenie CPU, RAM, dysku i czas od włączenia PC |
| `.switch` | Pokazuje listę monitorów |
| `.switch 0` | Ustawia pierwszy monitor do zrzutów |
| `.switch 1` | Ustawia drugi monitor do zrzutów |

### System i pliki
| Komenda | Do czego służy |
|---------|----------------|
| `.cmd <komenda>` | Uruchamia komendę systemową Windows |
| `.ls [ścieżka]` | Pokazuje pliki i foldery (działa też ze spacjami w nazwie) |
| `.download <ścieżka>` | Pobiera plik z komputera i wysyła na Discorda (limit ok. 24 MB) |
| `.upload` | Zapisuje plik wysłany na Discordzie na dysk komputera |
| `.procs` | Lista procesów zużywających najwięcej RAM |
| `.windows` | Lista otwartych okien |
| `.kill <nazwa>` | Zamyka proces (np. `.kill chrome`) |
| `.clipboard` | Pokazuje tekst ze schowka |

### Podgląd ekranu / kamery / mikrofonu
| Komenda | Do czego służy |
|---------|----------------|
| `.ss` | Zrzut ekranu |
| `.sslive on` | Co 3 sekundy wysyła nowy zrzut |
| `.sslive off` | Wyłącza ciągłe zrzuty |
| `.webcam` | Robi zdjęcie z kamerki |
| `.camrec 5` | Nagrywa 5 sekund wideo z kamerki (max 12 s) |
| `.mic 5` | Nagrywa 5 sekund dźwięku z mikrofonu (max 15 s) |
| `.choosemic` | Pokazuje listę mikrofonów |
| `.choosemic 2` | Wybiera mikrofon nr 2 |

### Dźwięk
| Komenda | Do czego służy |
|---------|----------------|
| `.soundplay` | Odtwarza załączony plik MP3/WAV na komputerze |
| `.soundstop` | Stopuje odtwarzanie |
| `.volume 50` | Ustawia głośność (0–100) |
| `.volup` | Zwiększa głośność |
| `.voldown` | Zmniejsza głośność |
| `.mute` | Wycisza / odcina wyciszenie |

### Zasilanie
| Komenda | Do czego służy |
|---------|----------------|
| `.lock` | Blokuje komputer |
| `.shutdown` | Wyłącza komputer za 10 sekund |
| `.restart` | Restartuje komputer za 10 sekund |
| `.battery` | Pokazuje poziom baterii (laptop) |

### Inne
| Komenda | Do czego służy |
|---------|----------------|
| `.open google.com` | Otwiera stronę w przeglądarce |
| `.notify cześć` | Pokazuje powiadomienie Windows |
| `.join` | Lista kanałów głosowych |
| `.join ogólny` | Bot wchodzi na kanał głosowy |
| `.leave` | Bot wychodzi z kanału głosowego |
| `.autoon` | Bot będzie startował razem z Windows |
| `.autooff` | Wyłącza auto-start |
| `.autostatus` | Sprawdza, czy auto-start jest włączony |
| `.destroy` | Całkowicie wyłącza bota |

---

## 2. Czego potrzebujesz

- Komputer z **Windows 10/11**
- Konto **Discord**
- **Python** (darmowy)
- Program do edycji kodu (polecane: **Visual Studio Code**)
- Plik `ochrona.py` (kod bota)

---

## 3. Krok po kroku – instalacja

### Krok A – Zainstaluj Python

1. Wejdź na stronę: https://www.python.org/downloads/
2. Kliknij żółty przycisk **Download Python**
3. Uruchom pobrany instalator
4. Na dole okna **zaznacz koniecznie**:
   - ✅ **Add python.exe to PATH**
5. Kliknij **Install Now**
6. Po instalacji otwórz **PowerShell** (Start → wpisz `PowerShell`) i wpisz:

```powershell
python --version
