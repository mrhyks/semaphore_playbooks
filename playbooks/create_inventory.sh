#!/bin/bash

# Run the Python script
python3 playbooks/create_inventory.py

# Check if the Python script ran successfully
if [ $? -eq 0 ]; then

    # Get the environment variable USER_EMAIL
    USER_EMAIL=${USER_EMAIL:-"default@example.com"}
    USER_NAME=${USER_NAME:-"default"}
    # Set the git configuration
    git config --global user.email "$USER_EMAIL"
    git config --global user.name "$USER_NAME"

    # Add changes to git
    git add .

    # Commit the changes
    git commit -m "Updated Ansible inventory"

    # Push the changes to the remote repository
    git push origin main
else
    echo "Python script failed to run."
    exit 1
fi