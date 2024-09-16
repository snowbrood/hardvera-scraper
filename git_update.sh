#!/bin/bash

# Configure git
git config --global user.name "github-actions"
git config --global user.email "github-actions@github.com"

# Fetch latest changes from the remote
git fetch origin main

# Stash any unstaged changes if they exist
git stash

# Create a temporary branch for the update
BRANCH_NAME="update-$(date +%s)-${RANDOM}"
git checkout -b $BRANCH_NAME

# Add changes to the CSV file
git add final_results.csv

# Commit the changes
git commit -m "Update CSV file"

# Rebase the temporary branch onto the latest main branch
git pull --rebase https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git main

# Push the changes to the temporary branch
git push https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git $BRANCH_NAME

# Merge the temporary branch into main
git checkout main
git pull --rebase https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git main
git merge $BRANCH_NAME --no-ff

# Push the changes to main
git push https://x-access-token:${PAT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git main

# Delete the temporary branch
git branch -d $BRANCH_NAME

# Apply any stashed changes (if there were any)
git stash pop || echo "No changes to pop from stash"
