#!/bin/bash

# Check if the folder path argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <folder_path>"
    exit 1
fi

# Get the folder path from the command-line argument
folder_path="$1"

# Generate a timestamp for the video file name
timestamp=$(date +"%Y%m%d%H%M%S")
output_video="$folder_path/video_$timestamp.mp4"

# FTP server details
#ftp_server="50.62.169.118:21"
#ftp_user="cctv"
#ftp_password="ai@camera"
#ftp_folder="/path/to/ftp/folder"

# Convert images to a video using ffmpeg
ffmpeg -framerate 8 -pattern_type glob -i "$folder_path/*.jpg" -c:v libx264 -pix_fmt yuv420p "$output_video"

# Upload the video file to the FTP server using curl
#curl --ftp-create-dirs -T "$output_video" -u "$ftp_user:$ftp_password" "ftp://$ftp_server/$ftp_folder/$(basename $output_video)"

# Delete all files in the input folder
#rm -f "$folder_path"/*

# Optionally, delete the output video file
# rm -f "$output_video"
