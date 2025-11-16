#!/bin/bash

# GitHub Repository Upload Script
# Run this script after creating your GitHub repository

set -e

echo "=========================================="
echo "GitHub Repository Upload Script"
echo "=========================================="
echo ""

# Check if repository URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./upload_to_github.sh <repository-url>"
    echo ""
    echo "Example:"
    echo "  ./upload_to_github.sh https://github.com/username/repo-name.git"
    echo "  OR"
    echo "  ./upload_to_github.sh git@github.com:username/repo-name.git"
    echo ""
    exit 1
fi

REPO_URL=$1

echo "Repository URL: $REPO_URL"
echo ""

# Check if remote already exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  Remote 'origin' already exists."
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "$REPO_URL"
        echo "✅ Remote URL updated"
    else
        echo "❌ Aborted"
        exit 1
    fi
else
    # Add remote
    echo "Step 1: Adding remote repository..."
    git remote add origin "$REPO_URL"
    echo "✅ Remote added"
fi

echo ""
echo "Step 2: Verifying remote..."
git remote -v
echo ""

echo "Step 3: Pushing code to GitHub..."
git push -u origin main

echo ""
echo "=========================================="
echo "✅ Upload complete!"
echo "=========================================="
echo ""
echo "Your repository is now available at:"
echo "$REPO_URL"
echo ""
echo "Please verify on GitHub that all files appear correctly."

