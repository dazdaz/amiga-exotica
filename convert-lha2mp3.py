#!/usr/bin/env python3
import os
import subprocess
import argparse
import tempfile
import multiprocessing
import signal
import sys

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def convert_to_mp3(full_path, sub, output_mp3):
    uade_cmd = ['uade123', '-f', '-', '-e', 'raw', '-s', str(sub), full_path]
    lame_cmd = ['lame', '-r', '-s', '44.1', '-m', 's', '-V', '2', '-', output_mp3]
    uade_proc = subprocess.Popen(uade_cmd, stdout=subprocess.PIPE)
    lame_proc = subprocess.Popen(lame_cmd, stdin=uade_proc.stdout)
    uade_proc.stdout.close()  # Allow uade_proc to receive a SIGPIPE if lame_proc exits
    uade_proc.wait()
    if uade_proc.returncode != 0:
        lame_proc.terminate()
        raise subprocess.CalledProcessError(uade_proc.returncode, uade_cmd)
    lame_proc.wait()
    if lame_proc.returncode != 0:
        raise subprocess.CalledProcessError(lame_proc.returncode, lame_cmd)

def main(paths):
    lha_paths = []
    for path in paths:
        if os.path.isdir(path):
            norm_path = os.path.normpath(path)
            if os.path.basename(norm_path).endswith('-skipthis'):
                continue
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.endswith('-skipthis')]
                for filename in files:
                    if filename.lower().endswith('.lha'):
                        lha_paths.append(os.path.join(root, filename))
        elif os.path.isfile(path) and path.lower().endswith('.lha'):
            lha_paths.append(path)
        else:
            raise ValueError(f"Invalid path: {path} is neither a directory nor an .lha file")
    if lha_paths:
        pool = multiprocessing.Pool(initializer=init_worker)
        try:
            pool.map(process_lha, lha_paths)
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, terminating workers")
            pool.terminate()
            pool.join()
            sys.exit(1)
        else:
            pool.close()
            pool.join()

def process_lha(lha_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the LHA archive to the temporary directory
        subprocess.run(['lha', f'xw={tmpdir}', lha_path], check=True)
        tasks = []
        processed_files = set()
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
                    min_sub = None
                    max_sub = None
                    for line in output.splitlines():
                        if line.startswith('subsongs:'):
                            parts = line.split()
                            min_sub = int(parts[2])
                            max_sub = int(parts[6])
                    if min_sub is not None and max_sub is not None:
                        num_subs = max_sub - min_sub + 1
                        print(f"File: {full_path} has {num_subs} subsongs")
                        processed_files.add(full_path)
                        for sub in range(min_sub, max_sub + 1):
                            tasks.append((full_path, sub))
                except subprocess.CalledProcessError:
                    print(f"Skipping {full_path} - not a valid music file for uade123")
                    os.remove(full_path)
        if tasks:
            output_dir = os.path.dirname(lha_path)
            archive_base = os.path.splitext(os.path.basename(lha_path))[0]
            # Sanitize archive_base
            archive_base = ''.join(c for c in archive_base if c.isalnum() or c in ['-', '_', ' ']).replace(' ', '_')
            total_songs = len(tasks)
            for idx, (full_path, sub) in enumerate(tasks):
                rel_path = os.path.relpath(full_path, tmpdir)
                if total_songs == 1:
                    output_mp3 = os.path.join(output_dir, f"{archive_base}.mp3")
                else:
                    output_mp3 = os.path.join(output_dir, f"{archive_base}_{idx + 1}.mp3")
                if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0:
                    print(f"Skipping {output_mp3} as it already exists and is not empty")
                    continue
                print(f"Converting: {rel_path} (subsong {sub}) to {output_mp3}")
                try:
                    convert_to_mp3(full_path, sub, output_mp3)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to convert {rel_path} (subsong {sub}) to {output_mp3}: {e}")
                    continue
        for f in processed_files:
            os.remove(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .lha files in directories or individual .lha files, extract, check subsongs, and convert them to MP3 using uade123 and lame in parallel.")
    parser.add_argument('paths', nargs='+', type=str, help="Paths to the directories containing .lha files or individual .lha files")
    args = parser.parse_args()
    main(args.paths)
