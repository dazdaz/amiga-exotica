# Amiga Music FTP Downloader 🎶

This Python script is a multi-threaded FTP downloader for Amiga music files (`.lha` archives) from the `UnExoticA/Game` directory on `ftp.exotica.org.uk`. It organizes downloads by author into a local `amiga_music_by_author` directory, supports pausing/resuming via a `progress.json` file, and handles connection errors gracefully.

---

## Features

* **Automated Organization:** Automatically organizes downloaded music files into author-specific folders.
* **Multi-threaded Downloads:** Uses a `ThreadPoolExecutor` (up to 3 parallel threads) to speed up the download process while respecting server connection limits.
* **Pause & Resume Functionality:** You can stop the script at any time (`Ctrl+C`) and it will save its progress. On the next run, it will resume downloading where it left off.
* **Robust Error Handling:** Automatically retries failed downloads up to 3 times with a random backoff delay. It also handles common FTP errors, such as "maximum clients reached."
* **Efficient & Smart:** Checks for existing files and compares local vs. remote file sizes to avoid re-downloading completed files and to resume partial downloads.

---

## How It Works

The script operates through several key components that manage the collection, downloading, and progress tracking.

### 1. File Collection (`collect_files`)
First, the script recursively traverses the FTP directory starting from `/pub/exotica/media/audio/UnExoticA/Game/`. It collects a list of all `.lha` files and maps their remote paths to a structured local path (`amiga_music_by_author/<Author>/<Filename>.lha`).

### 2. Progress Tracking (`save_progress` & `load_progress`)
The script uses a `progress.json` file to keep track of its state:
* **On startup**, it checks for `progress.json`.
* If the file exists, it loads the list of files to download and the set of already completed files, allowing you to resume a previous session.
* If the file doesn't exist, or if the user opts to re-scan, the script performs the file collection step and creates a new `progress.json`.
* Progress is automatically saved when the script is paused via `KeyboardInterrupt` (`Ctrl+C`).

### 3. Downloading (`download_file` & `main`)
The main function orchestrates the download process:
* It initializes a `ThreadPoolExecutor` to manage a pool of up to 3 worker threads.
* Each thread is assigned a file to download. It uses FTP binary mode and the `SIZE` and `REST` commands to handle resuming partial downloads.
* Global `to_download` and `completed` lists are shared across threads and protected by a lock to prevent race conditions.
* The script provides a summary of files to be downloaded and prompts the user before starting.

---

## Usage

1.  Make sure you have Python installed.
2.  Save the script in a directory of your choice.
3.  Run it from your terminal:
    ```sh
    python your_script_name.py
    ```
4.  Follow the on-screen prompts. You will be asked if you want to start downloading or rescan the server for files.
5.  To **pause** the download, press `Ctrl+C`. The script will catch the interruption, save its progress, and exit cleanly. You can run the script again later to resume.

```bash
./mirror-exotica.py
```

## Troubleshooting

* Show full path to files to download
```bash
jq '.to_download[].remote_path' progress.json
```

* Total number of files to download
```bash
jq '.to_download | length' progress.json
1999
```
