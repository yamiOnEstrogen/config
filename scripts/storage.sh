#!/bin/bash

# Function to convert space to GB or MB
convert_space() {
    local space_value=$1
    local space_in_gb
    local space_in_mb

    if [[ $space_value == *G ]]; then
        space_in_gb=$(echo $space_value | sed 's/G//')
        echo "${space_in_gb}GB"
    else
        space_in_mb=$(echo $space_value | sed 's/M//')
        echo "${space_in_mb}MB"
    fi
}

# Get used and free space on the root filesystem
USED_SPACE=$(df -h / | awk 'NR==2 {print $3}')
FREE_SPACE=$(df -h / | awk 'NR==2 {print $4}')
TOTAL_SPACE=$(df -h / | awk 'NR==2 {print $2}')

# Convert used, free, and total space to GB or MB
USED=$(convert_space "$USED_SPACE")
FREE=$(convert_space "$FREE_SPACE")
TOTAL=$(convert_space "$TOTAL_SPACE")

# Print the results
echo "Used: $USED"
echo "Free: $FREE"
echo "Total: $TOTAL"
