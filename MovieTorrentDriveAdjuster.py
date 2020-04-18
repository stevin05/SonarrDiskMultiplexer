import os
import sys
from pathlib import Path
import qbittorrentapi
import logging
import requests

# Prerequisites:
# 1. Install python
# 2. Make sure python is in the system path (a check box on the installation)
# 3. Install pip so you can grab the required packages
# 4. pip install requests
# 5. pip install qbittorrentapi
# 6. qbittorrent 'Downloads' settings:
#    a. Default Torrent Management Mode: Manual
#    b. Keep incomplete torrents in: <UNCHECKED>
#    c. Default Save Path -> One of the Downloads directories from step 7
# 7. Same directory structure on every drive. Something like:
#     X:/Downloads <Set one of these as the default in qbittorrent so radarr puts stuff there>
#     X:/Movies
#     Y:/Downloads
#     Y:/Movies
#     Z:/Downloads
#     Z:/Movies
# 8. RADARR -> Settings -> Connect -> Custom Script -> Path to this script. Check 'On Grab'
# 9. Set environment variables 'RADARR_API_KEY', 'QBT_USER', 'QBT_PORT', and 'QBT_PASSWORD' to match your API key
#    in RADARR and web UI settings in qbittorrent. Or just set them into the variables below.
# RADARR will find shows, start downloading them into qbittorrent's default directory and
# then call this script. This script will pause the torrent, move it to the same drive that
# the TV show would have eventually been copied to, and then resume it. When the download is
# complete, it's already on the correct drive and can now be hard linked instead of copied.

radarr_api_key = os.environ['RADARR_API_KEY']
qbt_user = os.environ['QBT_USER']
qbt_password = os.environ['QBT_PASSWORD']
qbt_port = os.environ['QBT_PORT']
log_file = 'C:\V2\Scripts\MovieTorrentDriveAdjuster.log'

# Some helper logging to figure out what our script parameters are
logging.basicConfig(
    filename=log_file,
    level=logging.WARNING,
    format='%(asctime)s %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S')

for env, value in os.environ.items():
    if env.startswith('RADARR'):
        logging.debug(f'[{env}: {value}]') 
        
event_type = os.environ['RADARR_EVENTTYPE']

if event_type != 'Grab':
    exit(0)

# Start by making sure we can talk to qbittorrent
qbt_client = qbittorrentapi.Client(host=f'localhost:{qbt_port}', username=qbt_user, password=qbt_password)
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# Grab the torrent object from qbittorrent so we can operate on it
torrents = qbt_client.torrents_info(hashes=[os.environ['RADARR_DOWNLOAD_ID'].lower()],limit=1)

# Make sure we found something
if len(torrents) != 1:
    msg = f"Couldn't relocate torrent for: {os.environ['RADARR_RELEASE_TITLE']}"
    print(msg)
    logging.error(msg)
    exit(1)

torrent = torrents[0]

# Pause the torrent. We hopefully catch this so early that the file is essentially empty.
try:
    torrent.pause()
except qbittorrentapi.APIError as e:
    msg = str(e)
    print(msg)
    logging.error(msg)
    
# Grab the full series info from RADARR. We weren't told where the show should go in our parameters.
movie_id = os.environ['RADARR_MOVIE_ID']
radarr_series = requests.get(
    f'http://localhost:7878/api/movie/{movie_id}',
    headers={'X-Api-Key': radarr_api_key},
)

new_location = None
old_location = None

if radarr_series.status_code == 200:
    drive = Path(radarr_series.json()['path']).parts[0]
    old_location = Path(torrent.save_path)
    old_parts = list(old_location.parts)
    old_parts[0] = drive
    new_location = Path(*old_parts)

else:
    msg = f'Failed to relocate: {os.environ["RADARR_RELEASE_TITLE"]}'
    print(msg)
    logging.error(msg)
    exit(1)


try:
    if new_location is not None:
        print(f'Moving {os.environ["RADARR_RELEASE_TITLE"]} from {old_location} to {new_location}')
        torrent.set_location(location=new_location)

    torrent.resume()
except qbittorrentapi.APIError as e:
    msg = str(e)
    print(msg)
    logging.error(msg)

  
