# Immich Album Downloader

This Python script downloads all assets (photos/videos) from a specific album in your [Immich](https://github.com/immich-app/immich) instance, using its API. It supports resuming by skipping files that already exist locally.

## Features

- Downloads all assets from a specified album
- Uses pagination to handle large albums
- Skips already-downloaded files
- Can be automated with `systemd` services and timers

## Requirements
You can install dependencies with:

```bash
pip install requests
```
or you can use your system's package manager.

## Environment Variables

| Variable               | Description                            |
|------------------------|----------------------------------------|
| `IMMICH_API_KEY`       | Your Immich API key                    |
| `IMMICH_INSTANCE_URL`  | Immich instance URL (e.g. `https://your-instance/api`) |
| `IMMICH_ALBUM_ID`      | The ID of the album to download        |
| `IMMICH_DOWNLOAD_PATH` | Directory to save downloaded assets    |

## Usage

You can run the script manually:

```bash
python3 main.py
```

Or set it up as a `systemd` service for automatic and scheduled execution.

---

## Running the script automatically

Create a service file at `/etc/systemd/user/immich-album-downloader.service`:

```ini
[Unit]
Description=Immich Album Downloader
After=network.target

[Service]
Type=simple
Environment="IMMICH_ALBUM_ID=my-super-cool-album-id"
Environment="IMMICH_API_KEY=averysecretapikeypleasedonotsteal"
Environment="IMMICH_DOWNLOAD_PATH=/home/marco/wallapers/"
Environment="IMMICH_INSTANCE_URL=https://your-immich.instance/api"
ExecStart=/usr/bin/python3 /opt/immich-album-downloader/main.py
Restart=no

[Install]
WantedBy=default.target
```

Enable and start the service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now immich-album-downloader.service
```

---

### Running the script periodically

To run the download periodically, create `/etc/systemd/user/immich-album-downloader.timer`:

```ini
[Unit]
Description=Download an Immich album periodically

[Timer]
OnBootSec=15m
OnUnitActiveSec=6h

[Install]
WantedBy=timers.target
```

Enable the timer:

```bash
systemctl --user enable --now immich-album-downloader.timer
```

This will trigger the album download 15 minutes after boot and then every 6 hours.

---