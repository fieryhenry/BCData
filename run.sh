#!/usr/bin/env bash

# cd to the directory of the script
cd "$(dirname "$0")"

# Update data
python3 run.py

# Add the new files to the repository
git add .

# Commit the changes
git commit -m "game data update (auto)"

# Push the changes
git push

# Upload the new apks to the internet archive
python3 archive_upload.py
