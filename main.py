import os
import requests
import logging
import time
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables
IMMICH_API_KEY = os.getenv('IMMICH_API_KEY')
IMMICH_INSTANCE_URL = os.getenv('IMMICH_INSTANCE_URL')
# ALBUM_NAME = os.getenv('IMMICH_ALBUM_NAME')
ALBUM_ID = os.getenv('IMMICH_ALBUM_ID')
DOWNLOAD_PATH = Path(os.getenv('IMMICH_DOWNLOAD_PATH', './downloads'))

def get_album_assets(album_id):
    """Retrieve all assets in album with pagination"""
    headers = {'x-api-key': IMMICH_API_KEY}
    assets = []
    page = 1

    while True:
        response = requests.get(
            f"{IMMICH_INSTANCE_URL}/albums/{album_id}",
            headers=headers,
            params={'page': page}
        )
        response.raise_for_status()

        assets.extend(response.json()["assets"])
        total_pages = int(response.headers.get('X-Pagination-Count', 1))
        if page >= total_pages:
            break
        page += 1
        # break

    return assets


def download_assets(assets):
    """Download missing assets to target directory"""
    DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
    headers = {'x-api-key': IMMICH_API_KEY}

    for asset in assets:
        filename = f"{asset['originalFileName']}"
        filepath = DOWNLOAD_PATH / filename

        if not filepath.exists():
            logging.info(f"Downloading {filename}")
            response = requests.get(
                f"{IMMICH_INSTANCE_URL}/assets/{asset['id']}/original",
                headers=headers,
                stream=True
            )
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            logging.debug(f"Skipping existing file {filename}")

if __name__ == "__main__":
    tryAgain = 5
    while tryAgain > 0:
        try:
            assets = get_album_assets(ALBUM_ID)
            download_assets(assets)
            logging.info(f"Sync complete. {len(assets)} assets processed")
            break
        except (requests.exceptions.ConnectionError, socket.gaierror, socket.timeout, TimeoutError) as e:
            logging.error(f"Error Network: {type(e).__name__}: {e}")
            if tryAgain == 0:
                logging.info("Max retries reached. Exiting.")
                break
            else:
                logging.info("Retrying in 5 minutes...")
            tryAgain -= 1
            time.sleep(300)        
        except Exception as e:
            logging.error(f"General Error: {type(e).__name__}: {e}")
            break