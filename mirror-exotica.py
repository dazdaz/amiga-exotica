#!/usr/bin/env python3
import ftplib
import os
import json
from typing import List, Dict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

PROGRESS_FILE = 'progress.json'
DOWNLOAD_DIR = 'amiga_music_by_author'
FTP_HOST = 'ftp.exotica.org.uk'
FTP_BASE_PATH = '/pub/exotica/media/audio/UnExoticA/Game/'
MAX_PARALLEL_DOWNLOADS = 3
MAX_RETRIES = 3
FTP_TIMEOUT = 30  # seconds

def collect_files(ftp: ftplib.FTP, current_path: str) -> List[Dict[str, str]]:
    files_to_download = []
    try:
        items = ftp.nlst()
    except ftplib.error_perm as e:
        if str(e).startswith('550'):
            return []  # No files or permission
        raise

    for item in items:
        try:
            ftp.cwd(item)
            # It's a directory, recurse
            sub_files = collect_files(ftp, os.path.join(current_path, item))
            files_to_download.extend(sub_files)
            ftp.cwd('..')
        except ftplib.error_perm:
            # It's a file
            if item.endswith('.lha'):
                remote_path = os.path.join(current_path, item)
                # Author is the parent dir name
                author = os.path.basename(os.path.dirname(remote_path))
                local_path = os.path.join(DOWNLOAD_DIR, author, item)
                files_to_download.append({'remote_path': remote_path, 'local_path': local_path})
    return files_to_download

def save_progress(to_download: List[Dict[str, str]], completed: set):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({'to_download': to_download, 'completed': list(completed)}, f)

def load_progress() -> tuple[List[Dict[str, str]], set]:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            return data['to_download'], set(data['completed'])
    return None, None

def download_file(file_info, lock):
    remote_path = file_info['remote_path']
    local_path = file_info['local_path']
    filename = os.path.basename(remote_path)
    for attempt in range(MAX_RETRIES):
        try:
            with ftplib.FTP(FTP_HOST, timeout=FTP_TIMEOUT) as ftp:
                ftp.login()
                ftp.cwd(os.path.dirname(remote_path))
                ftp.voidcmd('TYPE I')  # Switch to binary mode for SIZE command
                remote_size = ftp.size(filename)
                local_size = os.path.getsize(local_path) if os.path.exists(local_path) else 0
                if local_size == remote_size:
                    print(f"Skipping complete file: {local_path}")
                    with lock:
                        completed.add(remote_path)
                        save_progress(to_download, completed)
                    return
                if local_size > remote_size:
                    print(f"Local file larger than remote, deleting and restarting: {local_path}")
                    os.remove(local_path)
                    local_size = 0
                mode = 'ab' if local_size > 0 else 'wb'
                print(f"{'Resuming' if local_size > 0 else 'Downloading'} {remote_path} to {local_path} from byte {local_size}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, mode) as local_file:
                    if local_size > 0:
                        ftp.voidcmd('TYPE I')
                        ftp.voidcmd(f'REST {local_size}')
                    ftp.retrbinary(f"RETR {filename}", local_file.write)
            with lock:
                completed.add(remote_path)
                save_progress(to_download, completed)
            return
        except ftplib.all_errors as e:
            err_str = str(e)
            if '530' in err_str and 'maximum number of clients' in err_str:
                if attempt < MAX_RETRIES - 1:
                    sleep_time = random.uniform(1, 5)
                    print(f"Connection limit reached ({err_str}), retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    continue
            print(f"Error downloading {remote_path}: {e}")
            if attempt < MAX_RETRIES - 1:
                sleep_time = random.uniform(1, 5)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            raise

def main():
    global to_download, completed
    to_download, completed = load_progress()
    has_cache = to_download is not None
    if has_cache:
        print(f"Cached list found with {len(to_download)} files.")
        recollect_input = input("Recollect file list? (yes/no): ").strip().lower()
        recollect = recollect_input in ['yes', 'y']
    else:
        recollect = True

    with ftplib.FTP(FTP_HOST, timeout=FTP_TIMEOUT) as ftp:
        ftp.login()  # Anonymous login
        ftp.cwd(FTP_BASE_PATH)

        if recollect:
            print("Collecting list of files to download...")
            to_download = collect_files(ftp, FTP_BASE_PATH)
            completed = set()
            save_progress(to_download, completed)
            print(f"Found {len(to_download)} files to download.")

    # List what will be downloaded
    print(f"Total files to download: {len(to_download)}")
    print("Examples:")
    for file in to_download[:5] + to_download[-5:]:
        print(f"- {file['remote_path']} -> {file['local_path']}")

    proceed = input("Proceed with download? (yes/no): ").strip().lower()
    if proceed not in ['yes', 'y']:
        print("Download cancelled.")
        return

    pending = [f for f in to_download if f['remote_path'] not in completed]

    if not pending:
        print("All files already downloaded.")
        return

    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_DOWNLOADS) as executor:
        futures = [executor.submit(download_file, file_info, lock) for file_info in pending]
        for future in as_completed(futures):
            future.result()  # Raise any exceptions

    print("Download completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Download paused. Run the script again to resume.")
    except Exception as e:
        print(f"Error: {e}")
