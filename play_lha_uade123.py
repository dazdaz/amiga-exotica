#!/usr/bin/env python3
import os
import subprocess
import argparse
import tempfile
import signal
import sys
current_player = None
def signal_handler(sig, frame):
    global current_player
    print("Ctrl-C captured, exiting nicely...")
    if current_player:
        current_player.terminate()
    sys.exit(0)
def main(path):
    if os.path.isdir(path):
        # Process all .lha files in the directory
        for filename in os.listdir(path):
            if filename.lower().endswith('.lha'):
                lha_path = os.path.join(path, filename)
                process_lha(lha_path)
    elif os.path.isfile(path) and path.lower().endswith('.lha'):
        # Process the single .lha file
        process_lha(path)
    else:
        raise ValueError(f"Provided path is neither a directory nor an .lha file: {path}")
def process_lha(lha_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the LHA archive to the temporary directory
        subprocess.run(['lha', f'xw={tmpdir}', lha_path], check=True)
        # Walk through the extracted files
        for root, _, files in os.walk(tmpdir):
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    # Get info about subsongs
                    info_process = subprocess.run(
                        ['uade123', '--get-info', full_path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    output = info_process.stdout
                    # Parse the output
                    modulename = None
                    min_sub = None
                    max_sub = None
                    for line in output.splitlines():
                        if line.startswith('modulename:'):
                            modulename = line.split(':', 1)[1].strip()
                        if line.startswith('subsongs:'):
                            parts = line.split()
                            min_sub = int(parts[2])
                            max_sub = int(parts[6])
                    if min_sub is not None and max_sub is not None:
                        num_subs = max_sub - min_sub + 1
                        print(f"File: {full_path} has {num_subs} subsongs")
                        if modulename is None:
                            modulename = os.path.basename(full_path)
                        for sub in range(min_sub, max_sub + 1):
                            if num_subs > 1:
                                print(f"Playing: {modulename} (subsong {sub})")
                            else:
                                print(f"Playing: {modulename}")
                            # Use Popen to allow interrupting the player
                            global current_player
                            player = subprocess.Popen(['uade123', '-s', str(sub), full_path])
                            current_player = player
                            returncode = player.wait()
                            current_player = None
                            if returncode != 0:
                                raise subprocess.CalledProcessError(returncode, player.args)
                    # Remove the file after processing (whether played or not)
                    os.remove(full_path)
                except subprocess.CalledProcessError:
                    print(f"Skipping {full_path} - not a valid music file for uade123")
                    # Remove the file after processing (whether played or not)
                    os.remove(full_path)
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description="Process .lha files in a directory or a single .lha file, extract, check subsongs, and play them using uade123.")
    parser.add_argument('path', type=str, help="Path to the directory containing .lha files or a single .lha file")
    args = parser.parse_args()
    main(args.path)
