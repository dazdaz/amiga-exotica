# Amiga Exotica UnExotica Tools 🎶

A collection of Python scripts for downloading, playing, and converting classic Amiga game music from the UnExoticA archive.
https://www.exotica.org.uk/wiki/UnExoticA

---

## Tools Included 🛠️

### `mirror-exotica.py` 📥

This script mirrors Amiga music from the `UnExoticA/Game` directory on `ftp.exotica.org.uk`.

* **Multi-threaded Downloader:** Downloads files quickly. (Full download takes about 25 minutes).
* **Organized Structure:** Sorts all `.lha` music archives into a local `amiga_music_by_author/` directory.
* **Resumable:** Can be paused and resumed at any time thanks to a `progress.json` tracking file.
* **Robust:** Gracefully handles FTP connection errors and retries.



### `play_lha_uade123.py` ▶️

Plays all the music files contained within a single `.lha` archive without leaving temporary files behind.

* **Function:** Uses the `uade123` player to handle playback of native Amiga music formats.
* **Clean:** Automatically extracts tracks for playback and removes the temporary files afterward.

### `convert-lha2mp3.py` 🔄

Extracts and converts all playable music modules from a `.lha` archive into the `.mp3` format.

* **Function:** Leverages `uade123` to convert the native Amiga formats to a modern, compatible format.
* **Batch Processing:** Ideal for creating a complete MP3 library from your downloaded `.lha` archives.


---

## Sample

This is a sample of some excellent digital music from bygone days. Strangely enough, it never ages.
<video src="https://github.com/user-attachments/assets/6886278e-4dd0-4114-8eeb-85b939f2172b">controls</video>
