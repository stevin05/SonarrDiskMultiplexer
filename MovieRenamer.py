import os
import sys
from pathlib import Path
import logging
import requests

# The Organize button in my Radarr wasn't working, so wrote this to use
# the radarr API to make the file names nice. Of course, as soon as I
# ran this, radarr started working, so this is probably worthless.

radarr_api_key = os.environ['RADARR_API_KEY']

movies = requests.get(
    'http://localhost:7878/api/movie/',
    headers={'X-Api-Key': radarr_api_key},
)

extensions = [ '.mkv', '.avi', '.mp4' ]
bad_chars = [ '*', '.', '"', '/', '\\', '[', ']', ':', ';', '|', ',' ]

for movie in movies.json():
    title = f"{movie['title']} ({movie['year']})"
    
    for bad in bad_chars:
        title = title.replace(bad, '-')
     
    title = title.replace('.', ' ')
    
    old_path = Path(movie['path'])
    
    if not old_path.exists():
        # Must have failed to update radarr after a prior move
        continue
    
    if old_path.stem == title:
        print(f'Skipping {title}')
        continue
    
    print(f'Renaming {title}')
    old_parts = list(old_path.parts)
    new_path_parts = old_parts[:-1]
    new_path = Path(*new_path_parts)
    new_path /= title
    print(new_path)
    
    
    old_file = None
    for file in old_path.iterdir():
        if file.suffix in extensions:
            old_file = file
            break
            
    if old_file is None:
        print(f'Unknown file type for: {title}')
        continue

    new_file = new_path / (title + old_file.suffix)
    print(f'Moving {old_file} to {new_file}')
    
    if not new_path.exists():
        new_path.mkdir()

    old_file.rename(new_file)
    
    for file in old_path.iterdir():
        new_file = new_path / file.name
        file.rename(new_file)
    old_path.rmdir()
