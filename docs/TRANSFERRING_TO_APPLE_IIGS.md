# Transferring Images to Apple IIgs and Setting Desktop Background

## Overview

After creating .3200 files with gs-convert, you need to:
1. Create a ProDOS disk image containing your file
2. Transfer the image to your Apple IIgs (or emulator)
3. Set it as your desktop background in GS/OS

This guide covers all major platforms: **Windows, macOS (Intel & Apple Silicon), and Linux**.

---

## Part 1: Disk Image Tools

Before transferring to hardware, you need to create ProDOS disk images. Here are the best cross-platform tools:

### Tool Comparison

| Tool | Windows | macOS Intel | macOS Apple Silicon | Linux | GUI | CLI | Recommendation |
|------|---------|-------------|---------------------|-------|-----|-----|----------------|
| **CiderPress II** | ✅ | ✅ | ✅ CLI only | ✅ | Windows only | ✅ | Best modern tool |
| **AppleCommander** | ✅ | ✅ | ✅ Native | ✅ | ✅ | ✅ | Easiest cross-platform |
| **Cadius** | ✅ | ✅ | Compile | ✅ | ❌ | ✅ | Legacy but reliable |
| **CiderPress (original)** | ✅ | ⚠️ Rosetta | ⚠️ Rosetta | ❌ | ✅ | ❌ | Windows only (native) |

---

## Installing Disk Image Tools

### CiderPress II

**The modern successor to CiderPress with excellent cross-platform support.**

#### Windows
```powershell
# Download from GitHub releases
# https://github.com/fadden/CiderPress2/releases

# Extract and add to PATH, or run directly
cp2.exe --help
```

#### macOS (Intel & Apple Silicon)
```bash
# CLI version runs natively on Apple Silicon via .NET
# Download from https://github.com/fadden/CiderPress2/releases

# Make executable
chmod +x cp2
./cp2 --help

# Optional: move to /usr/local/bin for system-wide access
sudo mv cp2 /usr/local/bin/
```

#### Linux
```bash
# Download from GitHub releases
wget https://github.com/fadden/CiderPress2/releases/latest/download/cp2-linux-x64.zip
unzip cp2-linux-x64.zip
chmod +x cp2
sudo mv cp2 /usr/local/bin/

# Or use .NET SDK
dotnet tool install -g CiderPress2
```

**CiderPress II Common Commands:**
```bash
# Create new ProDOS disk
cp2 create-disk-image mydisk.po 800kb prodos

# Add file with ProDOS type
cp2 add mydisk.po yourimage.3200 --type C0 --aux 0000

# List contents
cp2 list mydisk.po

# Extract all files
cp2 extract mydisk.po

# Get detailed info
cp2 disk-info mydisk.po
```

---

### AppleCommander

**Java-based, works everywhere Java runs. Great for scripting.**

#### Windows
```powershell
# Option 1: Download JAR from GitHub
# https://github.com/AppleCommander/AppleCommander/releases

# Run directly
java -jar AppleCommander-win64-1.9.0.jar

# Or use the native .exe wrapper
AppleCommander-win64-1.9.0.exe
```

#### macOS (Intel)
```bash
# Using Homebrew
brew install applecommander

# Or download JAR
curl -LO https://github.com/AppleCommander/AppleCommander/releases/latest/download/AppleCommander-macos-x86_64.jar
java -jar AppleCommander-macos-x86_64.jar
```

#### macOS (Apple Silicon - M1/M2/M3/M4)
```bash
# Using Homebrew (RECOMMENDED - native ARM support)
brew install applecommander

# Or download native ARM JAR
curl -LO https://github.com/AppleCommander/AppleCommander/releases/latest/download/AppleCommander-macos-aarch64.jar
java -jar AppleCommander-macos-aarch64.jar

# Verify native
file AppleCommander-macos-aarch64.jar  # Should show ARM64
```

#### Linux
```bash
# Download appropriate architecture
# x86_64:
wget https://github.com/AppleCommander/AppleCommander/releases/latest/download/AppleCommander-linux-x86_64.jar

# ARM64 (Raspberry Pi, etc):
wget https://github.com/AppleCommander/AppleCommander/releases/latest/download/AppleCommander-linux-aarch64.jar

# Make wrapper script
echo '#!/bin/bash' > applecommander
echo 'java -jar /usr/local/share/AppleCommander.jar "$@"' >> applecommander
chmod +x applecommander
sudo mv applecommander /usr/local/bin/
```

**AppleCommander Common Commands:**
```bash
# Create new ProDOS disk
applecommander -pro mydisk.po MYDISK 800KB

# Add file (must use stdin redirection)
applecommander -p mydisk.po yourimage.3200 C0 0000 < yourimage.3200

# List contents
applecommander -l mydisk.po

# Extract file
applecommander -g mydisk.po yourimage.3200

# Detailed catalog
applecommander -ll mydisk.po
```

---

### Cadius

**Command-line only, part of Brutal Deluxe's Cross Development Tools.**

#### Windows
```powershell
# Download from Brutal Deluxe
# https://www.brutaldeluxe.fr/products/crossdevtools/cadius/

# Extract Cadius.exe to your PATH
cadius.exe HELP
```

#### macOS (Intel)
```bash
# Using maintained fork (recommended)
git clone https://github.com/mach-kernel/cadius.git
cd cadius
make
sudo cp cadius /usr/local/bin/

# Or download binary from Brutal Deluxe site
```

#### macOS (Apple Silicon)
```bash
# Compile from source (uses native ARM compiler)
git clone https://github.com/mach-kernel/cadius.git
cd cadius
make clean
make CC=clang
sudo cp cadius /usr/local/bin/

# Verify native
file cadius  # Should show arm64
```

#### Linux
```bash
# Compile from source
git clone https://github.com/mach-kernel/cadius.git
cd cadius
make
sudo make install

# Or use Docker
docker run -v $(pwd):/data mach-kernel/cadius --help
```

**Cadius Common Commands:**
```bash
# Create new ProDOS volume
CADIUS CREATEVOLUME mydisk.po MYDISK 800KB

# Add file
CADIUS ADDFILE mydisk.po /MYDISK yourimage.3200

# Set file type
CADIUS CHANGETYPE mydisk.po /MYDISK/YOURIMAGE.3200 C0 0000

# List contents
CADIUS CATALOG mydisk.po

# Extract file
CADIUS EXTRACTFILE mydisk.po /MYDISK/YOURIMAGE.3200 ./
```

---

## Part 2: Transfer Methods

### Method 1: Emulator (Easiest for Testing)

Test your images in an emulator before transferring to real hardware.

#### GSport / GSPlus

**Windows:**
```powershell
# Download GSport: https://apple2.gs/
# Create disk with CiderPress II
cp2 create-disk-image transfer.po 800kb prodos
cp2 add transfer.po desktop.3200 --type C0 --aux 0000

# Edit GSport config to mount transfer.po
# Start GSport
```

**macOS:**
```bash
# GSport works on Intel Macs
# For Apple Silicon, use UTM with emulation

# Create disk
cp2 create-disk-image transfer.po 800kb prodos
cp2 add transfer.po desktop.3200 --type C0 --aux 0000

# Launch GSport and mount transfer.po
```

**Linux:**
```bash
# Install GSport
sudo apt install gsport  # Debian/Ubuntu
# or build from source

# Create and mount disk
cp2 create-disk-image transfer.po 800kb prodos
cp2 add transfer.po desktop.3200 --type C0 --aux 0000
gsport
```

#### MAME (Multi-platform)

**All platforms:**
```bash
# Install MAME
# Windows: https://www.mamedev.org/
# Mac: brew install mame
# Linux: sudo apt install mame

# Run Apple IIgs
mame apple2gs -flop3 transfer.po
```

---

### Method 2: ADTPro (Audio/Serial Transfer to Real Hardware)

**ADTPro works on all platforms and is the most popular method for transferring to real Apple IIgs hardware.**

#### Requirements
- Modern computer (Windows/Mac/Linux)
- Apple IIgs with working disk drive
- Audio cable (3.5mm) OR USB-serial adapter
- ADTPro software (free)

#### Installation

**Windows:**
```powershell
# Download from http://adtpro.com/
# Extract ADTPro-2.1.0.zip
cd ADTPro-2.1.0
# Run ADTPro.bat
```

**macOS:**
```bash
# Download from http://adtpro.com/
curl -LO http://adtpro.com/releases/ADTPro-2.1.0.dmg
# Mount DMG and copy to Applications
# Or extract .zip version
```

**Linux:**
```bash
# Download
wget http://adtpro.com/releases/ADTPro-2.1.0.tar.gz
tar xzf ADTPro-2.1.0.tar.gz
cd ADTPro-2.1.0

# Run server
./adtpro.sh
```

#### Creating ADTPro Boot Disk

You need to write the ADTPro client disk to a physical floppy for your IIgs:

**Option A: Using Greaseweazle (recommended)**
```bash
# All platforms - Greaseweazle is best modern option
# https://github.com/keirf/greaseweazle

# Download ADTPro-2.1.0-140.dsk
# Write to 5.25" floppy:
gw write --format apple2.dos33 ADTPro-2.1.0-140.dsk

# Or 3.5" version:
# Download ADTPro-2.1.0.po
gw write --format apple2.prodos.800 ADTPro-2.1.0.po
```

**Option B: Using Applesauce**
```bash
# macOS/Windows - Commercial but excellent
# https://applesaucefdc.com/

# Use GUI to write ADTPro disk image
```

**Option C: Older PC with floppy drive**
```bash
# Windows with native floppy controller
# Use ADTPro's built-in disk writer
# Or use WinImage
```

#### Using ADTPro

**1. Connect Hardware:**

Audio method (slower, easier):
```
Computer headphone jack → 3.5mm cable → IIgs cassette input port
```

Serial method (faster, requires adapter):
```
Computer USB → USB-Serial adapter → IIgs modem or printer port
```

**2. On Modern Computer:**

**Windows:**
```powershell
cd ADTPro-2.1.0
ADTPro.bat

# In ADTPro window:
# - Select Audio or Serial
# - Configure COM port (if serial)
# - Wait for IIgs to connect
```

**macOS/Linux:**
```bash
cd ADTPro-2.1.0
./adtpro.sh

# In ADTPro window:
# - Select /dev/cu.usbserial (Mac) or /dev/ttyUSB0 (Linux) for serial
# - Or select audio
```

**3. On Apple IIgs:**
- Boot with ADTPro client disk
- Choose Audio or Serial mode to match computer
- Wait for connection
- Use ADTPro client to receive disk images

**4. Prepare Disk Image:**

**All platforms:**
```bash
# Create transfer disk with your image
cp2 create-disk-image transfer.po 800kb prodos
cp2 add transfer.po desktop.3200 --type C0 --aux 0000

# In ADTPro server:
# - Select "Send"
# - Choose transfer.po
# - IIgs will receive and write to floppy
```

---

### Method 3: CompactFlash / SD Card (Modern Storage)

If your Apple IIgs has a **CFFA3000**, **BOOTI**, or **Focus IDE** card with CF/SD adapter:

#### Windows

**Using CiderPress II:**
```powershell
# Create large ProDOS volume
cp2 create-disk-image cfcard.po 32mb prodos

# Add your images
cp2 add cfcard.po desktop.3200 --type C0 --aux 0000
cp2 add cfcard.po photo1.3200 --type C0 --aux 0000

# Write to CF card
# Use Win32DiskImager or dd for Windows
dd if=cfcard.po of=\\.\PhysicalDrive1 bs=512
```

#### macOS

```bash
# Create volume
cp2 create-disk-image cfcard.po 32mb prodos

# Add files
cp2 add cfcard.po desktop.3200 --type C0 --aux 0000

# Find CF card
diskutil list

# Unmount (not eject!)
diskutil unmountDisk /dev/disk2

# Write image
sudo dd if=cfcard.po of=/dev/rdisk2 bs=512

# Eject
diskutil eject /dev/disk2
```

#### Linux

```bash
# Create volume
cp2 create-disk-image cfcard.po 32mb prodos

# Add files
cp2 add cfcard.po desktop.3200 --type C0 --aux 0000

# Find device
lsblk

# Unmount if auto-mounted
sudo umount /dev/sdb*

# Write image
sudo dd if=cfcard.po of=/dev/sdb bs=512 status=progress

# Eject
sudo eject /dev/sdb
```

**Note**: Always unmount before writing with dd, and be VERY careful with device names!

---

### Method 4: Floppy Disk (If You Have the Hardware)

Modern USB floppy drives **DO NOT WORK** with Apple II disks. You need:

- Greaseweazle (~$20 DIY)
- Applesauce (~$100)
- Kryoflux (~$100+)
- Or old PC with native floppy controller

**Using Greaseweazle (all platforms):**
```bash
# Install Greaseweazle CLI
pip install greaseweazle

# Create disk image
cp2 create-disk-image transfer.po 800kb prodos
cp2 add transfer.po desktop.3200 --type C0 --aux 0000

# Write to 3.5" disk
gw write --format apple2.prodos.800 transfer.po

# Or write to 5.25" disk (convert to DOS 3.3 first)
# Note: .3200 files require ProDOS, so 3.5" disk recommended
```

---

### Method 5: Ethernet (If You Have AppleTalk/EtherTalk Card)

If your IIgs has **Uthernet II** or other Ethernet card:

#### Setting Up Netatalk Server

**macOS:**
```bash
# Install Netatalk
brew install netatalk

# Configure /usr/local/etc/afp.conf
# Share a folder accessible to IIgs
```

**Linux (Raspberry Pi, server, etc):**
```bash
# Install Netatalk 3
sudo apt install netatalk

# Edit /etc/netatalk/afp.conf
[APPLE2]
  path = /home/pi/apple2share
  valid users = pi

# Restart service
sudo systemctl restart netatalk
```

**On IIgs:**
- Install TCP/IP stack (Marinetti)
- Configure network settings
- Use AppleShare client to connect
- Copy files directly

---

## Part 3: Setting Desktop Background in GS/OS

Once your .3200 file is on the Apple IIgs:

### Important: Third-Party Software Required

**GS/OS does not include a built-in desktop picture control panel.** You need third-party utilities to set desktop backgrounds, even on GS/OS 6.0.4.

### Recommended Desktop Utilities

**DeskMaker** (Most Popular)
- Simple, lightweight desktop picture utility
- Easy to use - just select your .3200 file
- Works with GS/OS 6.0+
- Small memory footprint

**Spectrum** (Full-Featured)
- Complete desktop picture manager
- More control over desktop appearance
- Can load multiple graphics formats (SHR, 3200, 3201)
- Advanced options for positioning and display
- Recommended for power users

**DreamGrafix** (Graphics Viewer + Desktop Setter)
- View and convert SHR images
- Set desktop background from within viewer
- Supports multiple graphics formats
- Good all-in-one solution

**SuperConvert** (Converter + Desktop Setter)
- Convert between graphics formats
- Set as desktop background
- Useful if you work with multiple formats

### Where to Find Desktop Utilities

**Asimov Archive (Most Complete):**
```
FTP: ftp://ftp.apple.asimov.net/pub/apple_II/images/graphics/
Web: https://www.apple.asimov.net/
```

Look for files like:
- `DeskMaker.shk` or `DeskMaker.bxy`
- `Spectrum.shk` or `Spectrum.bxy`
- `DreamGrafix.shk`
- `SuperConvert.shk`

**Internet Archive:**
```
https://archive.org/details/apple_ii_library
Search for: "Apple IIgs desktop utilities" or "SHR viewer"
```

**Apple II Documentation Project:**
```
https://mirrors.apple2.org.za/
Navigate to: GS Software → Graphics Utilities
```

### Installing Desktop Utilities

Most utilities are distributed as ShrinkIt archives (.shk, .bxy):

1. **Download the utility** (e.g., DeskMaker.shk)

2. **Transfer to your IIgs** using your preferred method:
   - Create a disk image with the utility
   - Use the same transfer method you used for your .3200 file

3. **Extract on IIgs:**
   - You'll need **ShrinkIt GS** or **GS.Shrinkit** to extract .shk files
   - Double-click the .shk file to extract
   - Or use the ShrinkIt application

4. **Run the utility:**
   - Double-click the extracted application
   - Select your .3200 file
   - Click "Set Desktop" or similar option

### Using DeskMaker (Example)

1. Launch DeskMaker application
2. Click "Select Picture..." button
3. Navigate to your .3200 file
4. Select it and click "Open"
5. Desktop updates immediately
6. Quit DeskMaker (settings persist)

### File Type Requirements

Your .3200 file MUST have correct ProDOS attributes:

- **File Type**: `$C0` (SHR 320 mode)
- **Aux Type**: `$0000`

**Setting with CiderPress II:**
```bash
# When adding file
cp2 add mydisk.po desktop.3200 --type C0 --aux 0000
```

**Setting with AppleCommander:**
```bash
# Type and aux are parameters (note: requires stdin redirection)
java -jar /path/to/AppleCommander.jar -p mydisk.po desktop.3200 C0 0000 < desktop.3200
```

**Setting on IIgs (if wrong):**
1. Select file in Finder
2. Choose "Get Info" from File menu (or Command-I)
3. Set File Type to `$C0`
4. Set Aux Type to `$0000`
5. Close Info window

### Alternative: Manual Method (Advanced)

Some .3200 files with correct file types can be set by:
1. Double-clicking the .3200 file
2. If the system recognizes it, it may offer to set as desktop
3. This depends on having the right application registered for $C0 files

However, **using a dedicated utility like DeskMaker is more reliable.**

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Desktop picture doesn't appear | Verify file type ($C0), ensure exactly 32,768 bytes |
| Image corrupted/garbled | Re-transfer file, check for transfer errors |
| Can't find desktop utility | Download from Asimov archive, need DeskMaker or Spectrum |
| Can't extract .shk file | Need ShrinkIt GS to extract ShrinkIt archives |
| Out of memory error | Close applications, need 1MB+ RAM for desktop pictures |
| Colors look wrong | Re-convert with different quantization method |
| Image too dark | Re-convert with `--gamma 0.7` or `--brightness 1.3` |
| Desktop resets after reboot | Desktop utility may need to be in Startup folder |

---

## Part 4: Complete Workflows by Platform

### Windows Workflow

```powershell
# 1. Install tools
# Download CiderPress II or AppleCommander

# 2. Create your image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8 --preview preview.png

# 3. Create disk image
cp2 create-disk-image transfer.po 800kb prodos

# 4. Add file with correct type
cp2 add transfer.po desktop.3200 --type C0 --aux 0000

# 5. Verify
cp2 list transfer.po

# 6. Transfer via:
# - GSport emulator (mount transfer.po)
# - ADTPro (send to IIgs)
# - Write to CF card with Win32DiskImager
```

### macOS (Intel) Workflow

```bash
# 1. Install tools
brew install applecommander

# 2. Create image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8 --preview preview.png

# 3. Create disk
applecommander -pro transfer.po TRANSFER 800KB

# 4. Add file
applecommander -p transfer.po desktop.3200 C0 0000 < desktop.3200

# 5. Verify
applecommander -l transfer.po

# 6. Transfer via emulator, ADTPro, or CF card
```

### macOS (Apple Silicon M1/M2/M3) Workflow

```bash
# 1. Install tools (native ARM support!)
brew install applecommander

# 2. Create image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8 --preview preview.png

# 3. Create disk (runs natively on Apple Silicon)
applecommander -pro transfer.po TRANSFER 800KB

# 4. Add file
applecommander -p transfer.po desktop.3200 C0 0000 < desktop.3200

# 5. Verify
applecommander -l transfer.po

# 6. Transfer options:
# - MAME (Apple Silicon native)
# - ADTPro (runs natively)
# - CF card (native dd command)
```

### Linux Workflow

```bash
# 1. Install tools
# Option A: CiderPress II
wget https://github.com/fadden/CiderPress2/releases/latest/download/cp2-linux-x64.zip
unzip cp2-linux-x64.zip
sudo mv cp2 /usr/local/bin/

# Option B: AppleCommander
wget https://github.com/AppleCommander/AppleCommander/releases/latest/download/AppleCommander-linux-x86_64.jar
# Create wrapper script

# 2. Create image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8 --preview preview.png

# 3. Create disk
cp2 create-disk-image transfer.po 800kb prodos

# 4. Add file
cp2 add transfer.po desktop.3200 --type C0 --aux 0000

# 5. Verify
cp2 list transfer.po

# 6. Transfer via MAME, ADTPro, or Greaseweazle
```

---

## Part 5: Quick Reference

### File Specifications for Desktop Background

- **Format**: .3200 (SHR 320 mode uncompressed)
- **Size**: Exactly 32,768 bytes
- **ProDOS Type**: $C0
- **Aux Type**: $0000
- **Resolution**: 320×200 pixels
- **Colors**: 16 per scanline (up to 16 palettes)

### Recommended Tool Combinations

**For Beginners:**
- **Windows**: CiderPress II GUI + ADTPro
- **Mac**: AppleCommander + ADTPro
- **Linux**: CiderPress II CLI + ADTPro

**For Advanced Users:**
- **Windows**: Cadius (scripting) + CF card
- **Mac**: AppleCommander (Homebrew) + CF card
- **Linux**: cp2 (automation) + Greaseweazle

**For Apple Silicon Mac Users:**
- **AppleCommander** (native ARM) + ADTPro
- Or **CiderPress II CLI** (native via .NET)

---

## Part 6: Essential Downloads

### Disk Image Tools
- **CiderPress II**: https://github.com/fadden/CiderPress2/releases
- **AppleCommander**: https://applecommander.github.io/
- **Cadius**: https://www.brutaldeluxe.fr/products/crossdevtools/cadius/
- **CiderPress (original)**: http://a2ciderpress.com/

### Transfer Software
- **ADTPro**: http://adtpro.com/
- **Greaseweazle**: https://github.com/keirf/greaseweazle
- **Applesauce**: https://applesaucefdc.com/

### Emulators
- **GSport**: https://apple2.gs/
- **MAME**: https://www.mamedev.org/
- **Ample** (Modern Mac): https://github.com/ksherlock/ample

### Hardware
- **CFFA3000**: https://dreher.net/?s=projects/CFforAppleII
- **BOOTI**: https://gitlab.com/neurogenesis/booti
- **Uthernet II**: https://a2retrosystems.com/

---

## Part 7: Community Resources

### Forums & Help
- **r/apple2** (Reddit): Active community
- **AppleFritter Forums**: https://www.applefritter.com/
- **comp.sys.apple2** (Usenet): Still active!
- **Vintage Computer Federation Discord**: Large community

### Software Archives
- **Asimov**: ftp://ftp.apple.asimov.net/
- **Internet Archive Apple II Collection**: https://archive.org/details/apple_ii_library
- **Apple II Documentation Project**: https://mirrors.apple2.org.za/

### Hardware Resources
- **ReActiveMicro**: Modern Apple II hardware
- **A2Heaven**: European supplier
- **The Brewing Academy**: Hardware mods and upgrades

---

## Notes

- Always test in an emulator first before transferring to real hardware
- Desktop pictures require GS/OS 6.0+ and at least 1MB RAM
- Keep backup copies of your disk images
- Be patient with ADTPro audio transfers (very slow but reliable)
- Serial transfers with ADTPro are much faster than audio
- CF cards are the most convenient modern storage solution
- Greaseweazle is the best modern solution for writing real floppies
- The Apple IIgs community is very helpful - don't hesitate to ask!

---

## Platform-Specific Tips

### Windows
- Use CiderPress II GUI for easiest experience
- ADTPro works great with USB-serial adapters
- Win32DiskImager for writing CF cards

### macOS Intel
- Everything works via Rosetta if needed
- Homebrew makes tool installation easy
- Native apps available for most tools

### macOS Apple Silicon
- Use Homebrew for native ARM tools
- AppleCommander has native M1/M2/M3 support
- CiderPress II CLI is native via .NET
- MAME has Apple Silicon builds
- ADTPro runs natively

### Linux
- Most tools compile from source easily
- Great for automation and scripting
- Raspberry Pi makes excellent ADTPro server
- Native ARM support for ARM-based Linux

---

Happy converting! Your Apple IIgs desktop is about to look amazing! 🍎✨
