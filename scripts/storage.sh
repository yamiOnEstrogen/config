#!/bin/bash

# Function to convert space to GB or MB
convert_space() {
    local space_value=$1
    local space_in_gb
    local space_in_mb

    # Check if the space value has 'G' (indicating gigabytes)
    if [[ $space_value == *G ]]; then
        space_in_gb=$(echo $space_value | sed 's/G//')
        echo "${space_in_gb} gigabytes"
    else
        # If not in gigabytes, assume it's in megabytes
        space_in_mb=$(echo $space_value | sed 's/M//')
        echo "${space_in_mb} megabytes"
    fi
}

# Get disk space information for the root filesystem
disk_space_info=$(df -h / | awk 'NR==2 {print $2,$3,$4}')

# Extracting values for total, used, and free space
read -r TOTAL_SPACE USED_SPACE FREE_SPACE <<< "$disk_space_info"

# Convert used, free, and total space to GB or MB using the convert_space function
USED=$(convert_space "$USED_SPACE")
FREE=$(convert_space "$FREE_SPACE")
TOTAL=$(convert_space "$TOTAL_SPACE")

# Print informative results
echo "Disk Space Information for the Root Filesystem:"
echo "---------------------------------------------"
echo "Total Space: $TOTAL"
echo "Used Space:  $USED"
echo "Free Space:  $FREE"
echo "---------------------------------------------"
