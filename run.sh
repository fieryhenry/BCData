#!/usr/bin/env bash

# cd to the directory of the script
cd "$(dirname "$0")"

# Run the application
python3 download_apks.py

# Add the new files to the repository
git add .

# Commit the changes
git commit -m "game data update (auto)"

# Push the changes
git push
