#!/bin/bash

# Check for required parameters
if [ $# -ne 2 ]; then
    echo "Usage: $0 <commit-message> <version>"
    exit 1
fi

# Parameters
commit_message=$1
version=$2

# Push changes to repo
git add .
git commit -m "$commit_message"
git push

# Tag the new release
git tag -a "v$version" -m "$commit_message"
git push origin "v$version"

# Build and upload package
python setup.py sdist
twine upload dist/*
