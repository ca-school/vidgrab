#!/usr/bin/env bash
set -e

# Install Python packages
pip install -r requirements.txt

# Download ffmpeg binary (static build - no root needed)
mkdir -p ~/bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz
tar -xf /tmp/ffmpeg.tar.xz -C /tmp
cp /tmp/ffmpeg-*-amd64-static/ffmpeg ~/bin/ffmpeg
cp /tmp/ffmpeg-*-amd64-static/ffprobe ~/bin/ffprobe
chmod +x ~/bin/ffmpeg ~/bin/ffprobe
rm -rf /tmp/ffmpeg*

echo "✅ Build complete! ffmpeg installed."
