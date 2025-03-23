#!/bin/bash
# Simple script to push the cricket dashboard to GitHub

# Ask for GitHub username and repository name
read -p "Enter your GitHub username: " username
read -p "Enter the repository name: " repo_name

# Check if this is already a git repository
if [ ! -d .git ]; then
    # Initialize git repository
    git init
    
    # Set up remote
    git remote add origin "https://github.com/$username/$repo_name.git"
else
    echo "Git repository already initialized."
    
    # Check if the remote exists
    if ! git remote get-url origin &> /dev/null; then
        git remote add origin "https://github.com/$username/$repo_name.git"
    else
        echo "Remote origin already exists."
    fi
fi

# Add all files
git add .

# Commit
git commit -m "Cricket Team Owner Statistics Dashboard"

# Push to GitHub
git push -u origin main || git push -u origin master

echo "Repository pushed to GitHub: https://github.com/$username/$repo_name"
echo "Remember to set up GitHub Pages in your repository settings if you want to deploy it." 