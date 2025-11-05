#!/bin/bash
#
# A simple script to sync the EU_Forest_C_Input_NextGenC repository on Puhti.
# This script navigates to the repo directory and runs 'git pull'.

echo "==> Syncing repository: EU_Forest_C_Input_NextGenC..."

# --- Configuration ---
# The path to your repository
REPO_PATH="/scratch/project_2016105/EU_Forest_C_Input_NextGenC"

# The path to the custom key you created.
# If you moved this key to ~/.ssh/id_rsa (Solution 2), this is not needed.
CUSTOM_KEY_PATH="/scratch/project_2016105/Puhti_git"
# --- End Configuration ---


# --- SSH Key Check ---
# Check if the SSH agent is running and has keys
if ! ssh-add -l > /dev/null; then
  echo "--> SSH agent has no keys. Trying to add one..."
  
  # Check if the default key exists (from Solution 2)
  if [ -f ~/.ssh/id_rsa ]; then
    echo "--> Found default key (~/.ssh/id_rsa)."
    # Start the agent and add the key
    eval $(ssh-agent -s) > /dev/null
    ssh-add ~/.ssh/id_rsa
  
  # Else, check if the custom key path is valid (from Solution 1)
  elif [ -f "$CUSTOM_KEY_PATH" ]; then
    echo "--> Found custom key ($CUSTOM_KEY_PATH)."
    # Start the agent and add the key
    eval $(ssh-agent -s) > /dev/null
    ssh-add "$CUSTOM_KEY_PATH"
  
  else
    echo "--> WARNING: No SSH key found to add. 'git pull' might fail if agent is not running."
  fi
fi
# --- End Key Check ---


# --- Git Sync ---
# Check if the repository directory exists
if [ -d "$REPO_PATH" ]; then
  # Navigate to the repository directory
  cd "$REPO_PATH"
  
  echo "--> Running 'git pull' in $(pwd)..."
  # Run git pull to sync changes
  git pull
  
  echo "==> Sync complete."
else
  echo "==> ERROR: Repository path not found at $REPO_PATH"
  echo "==> Please update the 'REPO_PATH' variable in this script."
fi

# Go back to the original directory (optional, but good practice)
cd - > /dev/null