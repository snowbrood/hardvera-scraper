#!/bin/bash

# Configure git
git config --global user.name "github-actions"
git config --global user.email "github-actions@github.com"

# Fetch latest changes from remote
git fetch origin main

# Create a temporary branch for the update
BRANCH_NAME="update-$(date +%s)-${RANDOM}"
git checkout -b $BRANCH_NAME

# Add changes to the CSV file
git add data.csv

# Commit the changes
git commit -m "Update CSV file"

# Rebase onto the latest main branch
git pull --rebase https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git main

# Force push the changes to the temporary branch
git push https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git $BRANCH_NAME --force

# Merge the temporary branch into main
git checkout main
git pull --rebase https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git main
git merge $BRANCH_NAME --no-ff

# Push the changes to main
git push https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git main

# Delete the temporary branch
git branch -d $BRANCH_NAME
