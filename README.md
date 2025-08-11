# amiga-exotica

```bash
./mirror-exotica.py
```

* Show full path to files to download
```bash
jq '.to_download[].remote_path' progress.json
```

* Total number of files to download
```bash
jq '.to_download | length' progress.json
1809
```
