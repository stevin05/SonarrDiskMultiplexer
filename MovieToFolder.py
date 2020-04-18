import os
import sys
from pathlib import Path
import logging
import requests

# Convert  my_movie.mkv  to my_movie/my_movie.mkv so it's ready for import by radarr
# Run this from the directory with the movie files (like the staging directory)
for movie in Path('.').iterdir():
    if movie.is_dir():
        continue
    Path(movie.stem).mkdir()
    print(f'mkdir: {movie.stem}')
    target = Path(movie.stem) / movie.name
    print(f'rename: {target}')
    movie.rename(target)