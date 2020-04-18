
import os
import sys
from pathlib import Path
import logging
import requests

# I was completely redoing my library, so used this to take a diff of my old library
# vs what I had so far in my V2 library so I could delete the old one and rebuild it
# via sonarr (we have google fiber, so it's just good community service to delete all
# the old stuff and get it again in a few seconds and then hardlink it back into my
# nicely formatted library)

# New library drives
drives = [ 'U:', 'V:', 'W:', 'X:', 'Z:' ]

# Old library locations
shows = [ 'U:\TV Shows', 'W:\TV Shows' ]

torrent = {}    
for drive in drives:
    tv_shows = Path(*[drive, '/V2/TV Shows'])
    
    for tv_show in tv_shows.iterdir():
        torrent[tv_show.name] = 1
        
disk = {}            
for old_show in shows:
    for tv_show in Path(old_show).iterdir():
        disk[tv_show.name] = 1

print('Torrents not in current tv_shows dir')    
for tv_show in torrent:
    if tv_show not in disk:
        print(f'\t{tv_show}')
        
print('tv_shows not in torrents list')    
for tv_show in disk:
    if tv_show not in torrent:
        print(f'\t{tv_show}')      
  