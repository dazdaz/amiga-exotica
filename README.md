# Amiga Exotica Tools 🎶

This Python script is a multi-threaded FTP downloader for Amiga music files (`.lha` archives) from the `UnExoticA/Game` directory on `ftp.exotica.org.uk`. It organizes downloads by author into a local `amiga_music_by_author` directory, supports pausing/resuming via a `progress.json` file, and handles connection errors gracefully.

---

## Overview

* ***mirror-exotica.py*** Mirror ftp.exotica.org.uk` - takes about 25 minutes
* ***play_lha_uade123.py*** Play a .lha file using uade123
* ***convert-lha2mp3.py*** Converts all files within a compressed .lha file into .mp3
