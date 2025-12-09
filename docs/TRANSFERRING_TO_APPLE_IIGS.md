# Transferring Images to Apple IIgs and Setting Desktop Background

## Overview

After creating .3200 files with gs-convert, you need to:
1. Transfer the file to your Apple IIgs
2. Set it as your desktop background in GS/OS

## Part 1: Transfer Methods

### Method 1: Emulator (Easiest for Testing)

**GSport / GSPlus:**
1. Create a ProDOS disk image:
   ```bash
   # Using CiderPress (macOS/Windows/Linux)
   ciderpress -create mydisk.po 800k prodos
   ciderpress -add mydisk.po yourimage.3200
   ```

2. In GSport config, mount the disk image
3. Boot GS/OS and access the mounted disk

**MAME:**
1. Place .3200 file in a folder accessible to MAME
2. Use MAME's file manager to copy to virtual disk

### Method 2: ADTPro (Audio/Serial Transfer to Real Hardware)

**ADTPro** is the most popular method for transferring to real Apple IIgs hardware.

**Requirements:**
- Modern computer with audio output or USB-serial adapter
- Apple IIgs with working disk drive
- Audio cable or serial cable
- ADTPro software (free)

**Steps:**

1. **Download ADTPro**: http://adtpro.com/

2. **Create ADTPro boot disk**:
   - Download the ADTPro disk image
   - Write to a real 3.5" or 5.25" floppy using:
     - **Greaseweazle** (best option for Mac/PC)
     - **Applesauce**
     - **Kryoflux**
     - Or an older PC with real floppy drive

3. **Connect Apple IIgs**:
   - **Audio method**: 3.5mm audio cable from computer headphone jack to IIgs cassette input
   - **Serial method**: USB-serial adapter to IIgs modem or printer port

4. **Boot IIgs with ADTPro disk**

5. **On modern computer**:
   - Run ADTPro server
   - Create a new .po (ProDOS) disk image
   - Add your .3200 file to the image
   - Send the entire disk image to IIgs via ADTPro

6. **On IIgs**:
   - Receive the disk image
   - Write it to a physical floppy
   - Reboot with that disk

### Method 3: CompactFlash / SD Card (Modern Storage)

If your Apple IIgs has a **CFFA3000** or **BOOTI** card:

1. Format CF/SD card as ProDOS on your modern computer using **CiderPress**

2. Create a folder on the card:
   ```
   /IMAGES/
     yourimage.3200
   ```

3. Insert card into IIgs

4. Boot GS/OS and browse to the IMAGES folder

### Method 4: Floppy Disk (If You Have the Hardware)

**If you have a modern computer with a floppy drive:**

1. **Write ProDOS disk image**:
   ```bash
   # Create disk image
   ciderpress -create transfer.po 800k prodos
   ciderpress -add transfer.po yourimage.3200

   # Write to physical disk (macOS example)
   dd if=transfer.po of=/dev/rdisk2 bs=512
   ```

2. **Insert disk in Apple IIgs**

**Note**: Modern USB floppy drives typically DON'T work with Apple II disks. You need:
- An older PC with native floppy controller
- A Greaseweazle/Applesauce device
- Or a vintage Mac with SuperDrive

### Method 5: Ethernet (If You Have AppleTalk/EtherTalk)

If your IIgs has an Uthernet II or other Ethernet card:

1. Set up **netatalk** on a Linux/Mac server
2. Configure AppleTalk file sharing
3. Connect IIgs to network
4. Access shared folder from GS/OS Finder
5. Copy files directly

---

## Part 2: Setting Desktop Background in GS/OS

Once your .3200 file is on the Apple IIgs, here's how to set it as desktop background:

### Using Control Panel

**GS/OS System 6.0+:**

1. Boot into GS/OS

2. Open **Control Panel** from the Apple menu or Launcher

3. Select **Desktop** control panel

4. Look for **Desktop Pattern** or **Desktop Picture** option

5. Click **Change...** or **Select...**

6. Navigate to your .3200 file

7. Select it and click **Open** or **OK**

8. The desktop should update immediately

### File Naming Convention

GS/OS expects specific file types. Your .3200 file should have:

- **ProDOS file type**: `$C0` (SHR 320 mode uncompressed)
- **Auxiliary type**: `$0000`

To set these attributes:

**Using CiderPress (before transfer):**
```bash
# Set file type when adding to disk image
ciderpress -add mydisk.po yourimage.3200 -type C0 -aux 0000
```

**On GS/OS (using System Utilities):**
1. Select file in Finder
2. Choose **Get Info** from File menu
3. Set **File Type** to `$C0`
4. Set **Aux Type** to `$0000`

### Alternative: Desktop Manager

Some third-party utilities exist for managing desktop pictures:

- **Spectrum** - Desktop picture manager
- **NinjaForce Desktop** - Alternative desktop manager
- **DreamGrafix** - Advanced graphics viewer/setter

### Troubleshooting

**Desktop picture doesn't appear:**
- Verify file type is `$C0` (SHR 320)
- Ensure file is exactly 32,768 bytes
- Try rebooting GS/OS
- Make sure you have enough RAM (1MB+ recommended)

**Image appears corrupted:**
- Verify transfer completed successfully
- Check file size is exactly 32,768 bytes
- Try re-transferring

**Can't find Desktop control panel:**
- Ensure you're running GS/OS 6.0 or later
- Some earlier versions may not support desktop pictures
- Try a third-party utility

---

## Quick Reference: File Specifications

**For GS/OS Desktop Background:**
- **Format**: .3200 (SHR 320 mode)
- **Size**: Exactly 32,768 bytes
- **ProDOS Type**: $C0
- **Aux Type**: $0000
- **Resolution**: 320×200 pixels
- **Colors**: 16 per scanline (up to 16 palettes)

---

## Testing with Emulator First

**Recommended workflow:**

1. **Create image** with gs-convert:
   ```bash
   gs-convert convert photo.jpg desktop.3200 --preview preview.png
   ```

2. **Test in emulator** (GSport):
   - Create disk image with CiderPress
   - Add .3200 file
   - Boot GS/OS in emulator
   - Set as desktop background
   - Verify it looks good

3. **Transfer to real hardware** once confirmed

This saves time and physical media!

---

## Recommended Tools

### Essential:
- **CiderPress** - Disk image creation/management
  - http://ciderpress.sourceforge.net/
- **ADTPro** - File transfer to real hardware
  - http://adtpro.com/
- **GSport** or **MAME** - Emulator for testing
  - https://apple2.gs/

### Optional:
- **Greaseweazle** - Modern floppy imaging device
  - https://github.com/keirf/greaseweazle
- **Applesauce** - Professional floppy imaging
  - https://applesaucefdc.com/

---

## Common Workflows

### Workflow 1: Test in Emulator
```bash
# 1. Create image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8 --preview preview.png

# 2. Create disk image
ciderpress -create test.po 800k prodos

# 3. Add file with correct type
ciderpress -add test.po desktop.3200 -type C0 -aux 0000

# 4. Mount test.po in GSport
# 5. Boot GS/OS and set desktop background
```

### Workflow 2: Transfer to Real IIgs via ADTPro
```bash
# 1. Create image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8

# 2. Create disk image
ciderpress -create mydisk.po 800k prodos
ciderpress -add mydisk.po desktop.3200 -type C0 -aux 0000

# 3. Use ADTPro to send mydisk.po to IIgs
# 4. On IIgs, receive and write to floppy
# 5. Set as desktop background
```

### Workflow 3: Modern Storage (CF Card)
```bash
# 1. Create image
gs-convert convert photo.jpg desktop.3200 --gamma 0.8

# 2. Format CF card as ProDOS
ciderpress -create cfcard.po 32m prodos

# 3. Add file
ciderpress -add cfcard.po desktop.3200 -type C0 -aux 0000

# 4. Write cfcard.po to physical CF card
dd if=cfcard.po of=/dev/rdiskN bs=512

# 5. Insert in IIgs with CFFA3000
```

---

## Additional Resources

- **Apple IIgs System 6.0.1**: Required for desktop picture support
- **GS/OS Reference Manual**: Detailed file type information
- **Apple II Enthusiasts Facebook Group**: Active community for help
- **comp.sys.apple2**: Usenet newsgroup (still active!)
- **AppleFritter Forums**: Vintage Apple discussion

---

## Notes

- Desktop pictures consume RAM - ensure you have at least 1MB
- Some desktop patterns/colors may affect picture visibility
- Not all GS/OS versions support desktop pictures
- Third-party utilities may offer more flexibility
- Always test in emulator first to save time and media

---

## Troubleshooting Guide

| Problem | Solution |
|---------|----------|
| File won't transfer | Check cable connections, try different ADTPro mode |
| Desktop picture corrupted | Verify file size (32768 bytes), check file type ($C0) |
| Can't see Desktop option | Update to GS/OS 6.0+, check Control Panel presence |
| Image too dark | Re-convert with `--gamma 0.7` or `--brightness 1.3` |
| Colors look wrong | Try different quantization method (`--quantize global`) |
| Transfer very slow | ADTPro audio can be slow, consider serial or modern storage |

---

For more help, the Apple IIgs community is very active and helpful:
- Reddit: r/apple2
- Discord: Vintage Computer Federation
- Forums: AppleFritter.com
