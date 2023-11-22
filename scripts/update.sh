#!/bin/bash

# Echo that we are looking for updates
echo "Looking for updated packages"

# Update package list
sudo pacman -Sy > /dev/null

# Check for outdated packages
outdated_packages=$(pacman -Qu)

if [[ -n "$outdated_packages" ]]; then
    # Display packages that need updating
    echo "The following packages need updating:"
    echo "$outdated_packages"
    
    # Prompt user for update choice
    read -p "Do you want to update these packages? (y/n): " update_choice

    if [[ "$update_choice" == "y" || "$update_choice" == "Y" ]]; then
        # Update packages
        echo "Updating packages..."
        sudo pacman -Syu > /dev/null
        echo "Packages updated successfully."
    else
        echo "No packages were updated."
    fi
else
    echo "All packages are up to date."
fi
