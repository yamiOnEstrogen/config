#!/bin/bash

# Check if there are any zip files in the current directory
shopt -s nullglob
zip_files=(*.zip)
shopt -u nullglob

if [[ ${#zip_files[@]} -eq 0 ]]; then
    echo "No .zip files found in the current directory."
    exit 1
fi

# Determine the target directory
if [[ "$1" == "/new" ]]; then
    target_dir=""
else
    target_dir="$1"
fi

# Confirm with the user before unzipping
echo "The following .zip files will be extracted:"
printf "%s\n" "${zip_files[@]}"
if [[ -z "$target_dir" ]]; then
    echo "Target directory: Current directory"
else
    echo "Target directory: $target_dir"
fi

read -p "Do you want to proceed? (y/n): " user_input

if [[ "$user_input" != "y" && "$user_input" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# Unzip each file into the specified or current directory
for zipfile in "${zip_files[@]}"; do
    if [[ -z "$target_dir" ]]; then
        dir_name="${zipfile%.zip}"
    else
        dir_name="$target_dir/$(basename "${zipfile%.zip}")"
    fi

    mkdir -p "$dir_name"
    unzip -q "$zipfile" -d "$dir_name"
    
    if [[ $? -ne 0 ]]; then
        echo "Error extracting $zipfile"
    fi
done

echo "Extraction complete."

