# Amiga Music Player 🎵

Play compressed .lha files using uade123 without having to worry about decompressing them.

A Python script to extract and play music from Amiga LHA archives.

---

## Features

* **Input Handling**: Accepts a path via a command-line argument, which can be either a directory containing `.lha` files or a single `.lha` file. Raises a `ValueError` for invalid paths.

* **Archive Processing**: For directories, it iterates through all files ending in `.lha` (case-insensitive). For single files, it processes the file only if it has a `.lha` extension.

* **Temporary Extraction**: Uses a temporary directory (via `tempfile.TemporaryDirectory`) to extract the contents of each `.lha` archive using the `lha` command-line tool with the `xw=` option.

* **File Traversal**: Walks through the extracted files in the temporary directory using `os.walk` to process each one individually.

* **Music File Validation & Info Retrieval**: For each extracted file, it runs `uade123 --get-info` to check if it's a valid music file and to retrieve metadata like `modulename` and the subsong range (min and max).

* **Subsong Parsing**: Parses the output from `uade123` to extract the `modulename` and subsong details. It calculates the total number of subsongs from the given range.

* **Playback Functionality**: Plays each subsong using `uade123 -s <subsong>` via `subprocess.Popen`, allowing for interruptible playback. It waits for playback to complete before proceeding.

* **User Feedback**: Prints details such as the number of subsongs, the `modulename`, and the current playback status (including the current subsong number if applicable).

* **Error Handling**: Skips files that are not valid for `uade123` by catching `CalledProcessError` and prints a corresponding skip message.

* **File Cleanup**: Removes each processed file (whether played or skipped) from the temporary directory immediately after it is handled.

* **Graceful Termination**: Implements a `SIGINT` (Ctrl-C) signal handler to terminate the current player process and exit the script cleanly.

* **State Management**: Uses a global variable to track the current player process, allowing the signal handler to terminate it correctly upon exit.

* **Command-Line Interface**: Utilizes `argparse` to parse the required `path
