import os
import stat
import sys
from pathlib import Path

# This script hardlinks everything in each drive's downloads directory to its staging
# directory. From the staging directory, the files can then be moved to the correct
# final locations by other tools. This allows non-hardlink capable tools to work
# from the staging directory without actually copying any data. Once done, just delete
# anything extra to free up the tiny space used by the hardlinks if it bothers you, or
# just leave it around for next time.

drives = [ 'U:', 'V:', 'W:', 'X:' 'Z:' ]
extensions = [ '.mkv', '.avi', '.mp4' ]

for drive in drives:
    downloads = Path(*[drive, 'V2', 'Downloads'])
    staging = Path(*[drive, 'V2', 'Staging'])
    
    staging.mkdir(exist_ok=True)
    
    # Had some crazy permissions problems at some point, probably due to
    # parent directories with weird settings. Don't think this is actually
    # needed now. Windows is stupid.
    os.chmod(str(staging), stat.S_IWRITE)
    
    for file in downloads.glob('**/*'):
        parts = list(file.parts)
        parts[2] = 'Staging'
        staging = Path(*parts)
        
        if staging.suffix not in extensions:
            continue
        
        
        staging_dir = Path(staging.parent)
        
        staging_dir.mkdir(parents=True,exist_ok=True)
        os.chmod(str(staging_dir), stat.S_IWRITE)
        
        if staging.exists():
            os.chmod(str(staging), stat.S_IWRITE)
        print(f'Linking: {file} to {staging}')
        staging.unlink(missing_ok=True)
        file.link_to(staging)
        os.chmod(str(staging), stat.S_IWRITE)
        
