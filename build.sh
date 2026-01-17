#!/bin/bash
# Build script for Vercel - copy static files to public folder

echo "Copying static files..."
mkdir -p public/static
cp -r static/* public/static/

echo "Static files ready!"
