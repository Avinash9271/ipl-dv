# Simple GitHub Setup Guide

## Push to GitHub

There are two ways to push your project to GitHub:

### Option 1: Using the script

Run the provided script:
```
./push_to_github.sh
```

Follow the prompts to enter your GitHub username and repository name.

### Option 2: Manual commands

```bash
# Create a new repository on GitHub first (via the website)

# Initialize git in your project (if not already done)
git init

# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Add all files
git add .

# Commit
git commit -m "Cricket Team Owner Statistics Dashboard"

# Push to GitHub
git push -u origin main
```

## Setup GitHub Pages

1. Go to your repository on GitHub
2. Click on "Settings"
3. Navigate to "Pages" in the left sidebar
4. Under "Branch", select "main" (or your preferred branch)
5. Click "Save"

Your site will be published at `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`

## Running Locally

To run the dashboard locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python team_owner_stats.py
```

The dashboard will be available at http://127.0.0.1:8050/ 